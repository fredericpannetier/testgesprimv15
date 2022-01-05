# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError

class DiPurchaseGridWiz(models.TransientModel):
    _name = "di.purchase.grid.wiz"
    _description = "Wizard to import previous sales into new sale order"
    
    po_id = fields.Many2one("purchase.order", string="Purchase Order", required=True)        
    product_ids = fields.Many2many("product.template", string="Previous purchases")
    
    def di_grid_validate(self):
        po_line = self.env['purchase.order.line']
        po_line.order_id = self.po_id.id
        po_line.company_id = self.po_id.user_id.company_id.id
        for product in self.product_ids:
            prod = self.env['product.product'].search([('product_tmpl_id','=',product.id)],limit=1)
            date_planned = self.po_id.date_planned or po_line._convert_to_middle_of_day(datetime.today())
            vals = {
                        'order_id': self.po_id.id,
                        'date_planned': date_planned,
                        'product_id': prod.id,
                        'product_uom':product.uom_id.id,
                        'name':product.name,
                        'product_qty': 0.0, 
                        'price_unit':product.standard_price                                                               
                    }
            self.po_id.order_line.create(vals)
        sql = """DELETE from di_purchase_grid_wiz where po_id = %s"""
        self.env.cr.execute(sql,(self.po_id.id,))

    @api.model
    def default_get(self, fields):
        res = super(DiPurchaseGridWiz, self).default_get(fields) 
        order = self.env['purchase.order'].browse(self.env.context.get('active_id')) # la commande est sauvegardée quand on clique sur le bouton grid de vente        
        partner_id = order.partner_id
        res['po_id']=order.id        
        grid_mode = self.env['ir.config_parameter'].sudo().get_param('purchase_grid.di_purch_grid_mode')        
        horizon = int(self.env['ir.config_parameter'].sudo().get_param('purchase_grid.di_purch_horizon'))
        order_num = int(self.env['ir.config_parameter'].sudo().get_param('purchase_grid.di_purch_order_num'))
        lines = self.env['purchase.order.line']
        if grid_mode=='Horizon':
            horizon_date = datetime.today() + timedelta(days=-horizon)                
            lines = self.env['purchase.order.line'].search(['&',('company_id','=',self.env.user.company_id.id),('order_id.partner_id','=',partner_id.id)]).filtered(lambda l: l.order_id.date_order>=horizon_date)
        elif grid_mode=='Order Number':
            if order_num !=0:
                NbOrders = order_num
            else:
                NbOrders = 1
            order_ids = self.env['purchase.order'].search(['&',('company_id','=',self.env.user.company_id.id),('partner_id','=',partner_id.id),('order_line','!=',False)],limit=NbOrders,order='id desc')
            lines = self.env['purchase.order.line'].search(['&',('company_id','=',self.env.user.company_id.id),('order_id.id','in',order_ids.ids)])

        Product_ids=[]
        if lines:
            for line in lines:
                Product_ids.append(line.product_id.product_tmpl_id.id)            
        if Product_ids: 
            res.update({'product_ids':[(6,0,list(set(Product_ids)))]})      
        return res    
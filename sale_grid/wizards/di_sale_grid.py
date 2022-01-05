# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError


class DiSaleGridWiz(models.TransientModel):
    _name = "di.sale.grid.wiz"
    _description = "Wizard to import previous sales into new sale order"

    so_id = fields.Many2one("sale.order", string="Sale Order", required=True)
    product_ids = fields.Many2many("product.template", string="Previous sales")

    def di_grid_validate(self):
        for product in self.product_ids:
            prod = self.env['product.product'].search(
                [('product_tmpl_id', '=', product.id)], limit=1)
            vals = {
                'order_id': self.so_id.id,
                'product_id': prod.id,
                'product_uom_qty': 0.0,
            }
            self.so_id.order_line.create(vals)
        sql = """DELETE from di_sale_grid_wiz where so_id = %s"""
        self.env.cr.execute(sql, (self.so_id.id,))

    @api.model
    def default_get(self, fields):
        res = super(DiSaleGridWiz, self).default_get(fields)
        # la commande est sauvegardée quand on clique sur le bouton grille de vente
        order = self.env['sale.order'].browse(
            self.env.context.get('active_id'))
        partner_id = order.partner_id
        res['so_id'] = order.id
        grid_mode = self.env['ir.config_parameter'].sudo(
        ).get_param('sale_grid.di_sale_grid_mode')
        sale_horizon = int(self.env['ir.config_parameter'].sudo(
        ).get_param('sale_grid.di_sale_horizon'))
        order_num = int(self.env['ir.config_parameter'].sudo(
        ).get_param('sale_grid.di_sale_order_num'))
        lines = self.env['sale.order.line']
        if grid_mode == 'Horizon':
            horizon_date = datetime.today() + timedelta(days=-sale_horizon)
            lines = self.env['sale.order.line'].search(['&', ('company_id', '=', self.env.user.company_id.id), (
                'order_id.partner_id', '=', partner_id.id)]).filtered(lambda l: l.order_id.date_order >= horizon_date)
        elif grid_mode == 'Order Number':
            if order_num != 0:
                NbOrders = order_num
            else:
                NbOrders = 1
            order_ids = self.env['sale.order'].search(['&', ('company_id', '=', self.env.user.company_id.id), (
                'partner_id', '=', partner_id.id), ('order_line', '!=', False)], limit=NbOrders, order='id desc')
            lines = self.env['sale.order.line'].search(
                ['&', ('company_id', '=', self.env.user.company_id.id), ('order_id.id', 'in', order_ids.ids)])

        Product_ids = []
        if lines:
            for line in lines:
                Product_ids.append(line.product_id.product_tmpl_id.id)

        if Product_ids:
            res.update({'product_ids': [(6, 0, list(set(Product_ids)))]})
        return res

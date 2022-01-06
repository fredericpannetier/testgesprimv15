# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class GesSaleStat(models.Model):
    _name = "ges.sale.stat"
    _description = "Sales Stat"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    @api.model
    def _get_done_states(self):
        return ['sale', 'done', 'paid']

    name = fields.Char('Order Reference', readonly=True)
    date = fields.Datetime('Order Date', readonly=True)
    product_id = fields.Many2one('product.product', 'Product Variant', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    # qty_delivered = fields.Float('Qty Delivered', readonly=True)
    # qty_to_invoice = fields.Float('Qty To Invoice', readonly=True)
    # qty_invoiced = fields.Float('Qty Invoiced', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    country_id = fields.Many2one('res.country', 'Customer Country', readonly=True)        
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True)
    ges_gweight = fields.Float('Gross Weight', readonly=True)
    ges_nweight = fields.Float('Net Weight', readonly=True)
    ges_pack = fields.Float(string="Packages",
                            help="""Number of packages""", digits=(12, 2))
    ges_piece = fields.Integer(string="Pieces",
                               help="""Number of pieces""")
    order_id = fields.Many2one('sale.order', 'Order #', readonly=True)
    commitment_date = fields.Datetime('Delivery date')
    lot_id = fields.Many2one('stock.production.lot', string='Lot', readonly=True)

    @property
    def _table_query(self):
        return '%s %s' % (self._select(), self._from())

    @api.model
    def _select(self):
        return  '''
            SELECT 
                l.id as id,
                l.product_id as product_id,
                t.uom_id as product_uom,
                CASE WHEN l.product_id IS NOT NULL THEN (sml.product_uom_qty / u.factor * u2.factor) ELSE 0 END as product_uom_qty,
                CASE WHEN l.product_id IS NOT NULL THEN (sml.ges_pack / u.factor * u2.factor) ELSE 0 END as ges_pack,
                CASE WHEN l.product_id IS NOT NULL THEN (sml.ges_piece / u.factor * u2.factor) ELSE 0 END as ges_piece,
                CASE WHEN l.product_id IS NOT NULL THEN (sml.ges_nweight / u.factor * u2.factor) ELSE 0 END as ges_nweight,
                CASE WHEN l.product_id IS NOT NULL THEN (sml.ges_gweight / u.factor * u2.factor) ELSE 0 END as ges_gweight,                
                s.name as name,
                s.date_order as date,
                s.commitment_date as commitment_date,
                s.state as state,
                s.partner_id as partner_id,            
                s.company_id as company_id,                        
                t.categ_id as categ_id,
                s.pricelist_id as pricelist_id,            
                p.product_tmpl_id,
                partner.country_id as country_id,            
                partner.commercial_partner_id as commercial_partner_id,                                    
                s.id as order_id,
                sml.lot_id as lot_id
        '''

    @api.model
    def _from(self):
        return """
        FROM
                sale_order_line l
                      right outer join sale_order s on (s.id=l.order_id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join uom_uom u on (u.id=l.product_uom)
                    left join uom_uom u2 on (u2.id=t.uom_id)
                    LEFT JOIN stock_move as sm on sm.sale_line_id = l.id 
                    LEFT JOIN stock_move_line sml on sml.move_id = sm.id
        """  
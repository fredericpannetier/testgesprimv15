# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class GesPrintInventoryWiz(models.TransientModel):
    _name = "ges.print.inventory.wiz"
    _description = "Print inventory"

    def _default_date_init(self):
        return datetime.today().date()
    company_id = fields.Many2one('res.company', string='Company', readonly=True,  default=lambda self: self.env.user.company_id)
    product_ids = fields.Many2many(
        "product.product", string="Products to print", domain="[('qty_available', '>', 0)]")
    category_ids = fields.Many2many(
        "product.category", string="Categories of products to print")
    lot_detail = fields.Boolean("Print lot detail", default=False)
    quant_ids = fields.Many2many("stock.quant")
    date = fields.Date(string="Date", default=_default_date_init)
    currency_symbol = fields.Char(string='Currency', related='company_id.currency_id.symbol')

    def print_inventory(self):
        #         quants = self.env['stock.quant'].search([('location_id.usage','=', 'internal')])
        #         if self.product_ids:
        #             quants2 = quants.filtered(lambda q: q.product_id in self.product_ids)
        #         else:
        #             quants2 = quants
        #
        #         if self.category_ids:
        #             quants3 = quants2.filtered(lambda q: q.product_id.ges_category_id in self.category_ids)
        #         else:
        #             quants3 = quants2
        #
        #         self.quant_ids = quants3

        if self.product_ids:
            if self.category_ids:
                self.quant_ids = self.env['stock.quant'].search([('location_id.usage', '=', 'internal'), (
                    'product_id', 'in', self.product_ids.ids), ('product_id.ges_category_id', 'in', self.category_ids.ids), ('company_id', '=', self.company_id.id)])
            else:
                self.quant_ids = self.env['stock.quant'].search(
                    [('location_id.usage', '=', 'internal'), ('product_id', 'in', self.product_ids.ids), ('company_id', '=', self.company_id.id)])
        else:
            if self.category_ids:
                self.quant_ids = self.env['stock.quant'].search(
                    [('location_id.usage', '=', 'internal'), ('product_id.ges_category_id', 'in', self.category_ids.ids), ('company_id', '=', self.company_id.id)])
            else:
                self.quant_ids = self.env['stock.quant'].search(
                    [('location_id.usage', '=', 'internal'), ('company_id', '=', self.company_id.id)])

        return self.env.ref('ges_stock.ges_action_report_inventory').report_action(self)

# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    def ges_get_outgoing_qty_draft(self, from_date=False, to_date=False):
        domain = [('product_id', 'in', self.ids),
                  ('state', 'in', ('draft', 'sent'))]
        if from_date:
            domain += [('ges_commitment_date', '>=', from_date)]
        if to_date:
            domain += [('ges_commitment_date', '<=', to_date)]
        sols = self.env['sale.order.line'].search(domain)
        qty = 0.0
        if sols:
            qty = sum([sol.product_uom_qty for sol in sols])
        return qty

    def ges_get_incoming_qty_draft(self, from_date=False, to_date=False):
        domain = [('product_id', 'in', self.ids),
                  ('state', 'in', ('draft', 'sent', 'to approve'))]
        if from_date:
            domain += [('date_planned', '>=', from_date)]
        if to_date:
            domain += [('date_planned', '<=', to_date)]
        pols = self.env['purchase.order.line'].search(domain)
        qty = 0.0
        if pols:
            qty = sum([pol.product_qty for pol in pols])
        return qty

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        res = super(ProductProduct, self)._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date, to_date)

        if self._context.get('ges_draft') and self._context.get('ges_draft') is True:
            for product in self.with_context(prefetch_fields=False):
                product_id = product.id
                rounding = product.uom_id.rounding
                res[product_id]['incoming_qty'] = res[product_id]['incoming_qty'] + \
                    float_round(product.ges_get_incoming_qty_draft(from_date, to_date),
                                precision_rounding=rounding)
                res[product_id]['outgoing_qty'] = res[product_id]['outgoing_qty'] + \
                    float_round(product.ges_get_outgoing_qty_draft(from_date, to_date),
                                precision_rounding=rounding)
                res[product_id]['virtual_available'] = float_round(
                    res[product_id]['qty_available'] +
                    res[product_id]['incoming_qty'] -
                    res[product_id]['outgoing_qty'],
                    precision_rounding=rounding)
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ges_category_id = fields.Many2one('di.multi.table', string='Category', domain=[
                                      ('record_type', '=', 'category')], help="The category of the product.")
    ges_origin_id = fields.Many2one('di.multi.table', string='Origin', domain=[
                                    ('record_type', '=', 'origin')], help="The Origin of the product.")
    ges_brand_id = fields.Many2one('di.multi.table', string='Brand', domain=[
                                   ('record_type', '=', 'brand')], help="The Brand of the product.")
    ges_size_id = fields.Many2one('di.multi.table', string='Size', domain=[
                                  ('record_type', '=', 'size')], help="The Size of the product.")


#     ges_category_id = fields.Many2one("ges.category",string="Catégory")
    ges_category_des = fields.Char(related='ges_category_id.name')

#     ges_origin_id = fields.Many2one("ges.origin",string="Origin")
    ges_origin_des = fields.Char(related='ges_origin_id.name')

#     ges_brand_id = fields.Many2one("ges.brand",string="Brand")
    ges_brand_des = fields.Char(related='ges_brand_id.name')

#     ges_size_id = fields.Many2one("ges.size",string="Size")
    ges_size_des = fields.Char(related='ges_size_id.name')

    ges_packaging_id = fields.Many2one("ges.packaging", string="Packaging")
    ges_packaging_des = fields.Char(related='ges_packaging_id.des')

    ges_pob = fields.Integer(string="Per outer box",
                             default=1, help="Number of products per outer box")
    ges_uweight = fields.Float(
        string="Unit weight", help="Weight per product", digits='Stock Weight')

    # def action_open_product_lot(self):
    #     self.ensure_one()
    #     action = self.env["ir.actions.actions"]._for_xml_id("stock.action_production_lot_form")
    #     action['domain'] = [('product_id', '=', self.id)]
    #     action['context'] = {
    #         'default_product_id': self.id,
    #         'set_product_readonly': True,
    #         'default_company_id': (self.company_id or self.env.company).id,
    #         'search_default_available': 1,
    #     }
    #     return action

    def action_open_product_lot(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_production_lot_form")
        action['domain'] = [('product_id.product_tmpl_id', '=', self.id)]
        action['context'] = {
            'default_product_tmpl_id': self.id,
            'default_company_id': (self.company_id or self.env.company).id,
            'search_default_available': 1,
        }
        if self.product_variant_count == 1:
            action['context'].update({
                'default_product_id': self.product_variant_id.id,
                'search_default_available': 1,
            })
        return action

    def get_packs_qty(self, qty):
        self.ensure_one()
        pack = 0.0
        if self.uom_id.ges_unittype == 'Piece':
            if self.ges_pob and self.ges_pob != 0:
                pack = round(qty/self.ges_pob)
        elif self.uom_id.ges_unittype == 'Package':
            pack = round(qty)
        elif self.uom_id.ges_unittype == 'Net weight':
            if self.ges_uweight and self.ges_uweight != 0:
                piece = 0
                piece = qty/self.ges_uweight
                if piece != 0 and self.ges_pob and self.ges_pob != 0:
                    pack = round(piece/self.ges_pob)
        return pack

    def get_pieces_qty(self, qty):
        self.ensure_one()
        piece = 0
        if self.uom_id.ges_unittype == 'Piece':
            piece = round(qty)
        elif self.uom_id.ges_unittype == 'Package':
            if self.ges_pob:
                piece = round(qty*self.ges_pob)
        elif self.uom_id.ges_unittype == 'Net weight':
            if self.ges_uweight and self.ges_uweight != 0:
                piece = round(qty/self.ges_uweight)
        return piece

    def get_nweight_qty(self, qty):
        self.ensure_one()
        weight = 0.0
        if self.uom_id.ges_unittype == 'Piece':
            if self.ges_uweight:
                weight = round(qty*self.ges_uweight, 3)
        elif self.uom_id.ges_unittype == 'Package':
            #             piece = 0
            if self.ges_pob and self.ges_pob != 0:
                #                 piece = qty/self.ges_pob
                if self.ges_uweight:
                    weight = round(qty*self.ges_uweight, 3)
        elif self.uom_id.ges_unittype == 'Net weight':
            weight = round(qty, 3)
        return weight


class GesPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    ges_uom = fields.Char(string='Unit of Measure Name', related='product_tmpl_id.uom_name', readonly=True)    

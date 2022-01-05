# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm, Warning

import logging

_logger = logging.getLogger(__name__)


class DiDefaultNote(models.Model):
    _name = 'di.default.note'
    _description = "Default note"
    _order = 'item'

    def _get_item(self):
        # fonction à surcharger selon les besoins
        item_vals = [("company", "Company"), ("partnertag", "Partner tag"), ("partner",
                                                                             "Partner"), ("productcat", "Product category"), ("product", "Product")]
        return item_vals

    def _get_item_value(self):
        value = ''
        if self.item == 'company':
            value = self.company_id.name
        elif self.item == 'partnertag':
            value = self.partnertag_id.name
        elif self.item == 'partner':
            value = self.partner_id.name
        elif self.item == 'productcat':
            value = self.productcat_id.name
        elif self.item == 'product':
            value = self.product_id.name
        return value

    @api.depends('item', 'company_id', 'partner_id', 'partnertag_id', 'product_id', 'productcat_id')
    def _compute_name(self):
        for note in self:
            note.name = note.item + ' ' + note._get_item_value()

    name = fields.Char(string='Name', compute="_compute_name", store=True)
    text = fields.Html(string="Text to print", required=True)
    so_print = fields.Boolean(string="Print on sale order")
    po_print = fields.Boolean(string="Print on purchase order")
    dn_print = fields.Boolean(string="Print on delivery note")
    inv_print = fields.Boolean(string="Print on invoice")
    item = fields.Selection('_get_item', string="Item", required=True)
    company_id = fields.Many2one('res.company', string='Company')
    partner_id = fields.Many2one('res.partner', string='Partner')
    partnertag_id = fields.Many2one(
        'res.partner.category', string='Partner tag')
    product_id = fields.Many2one('product.product', string='Product')
    productcat_id = fields.Many2one(
        'product.category', string='Product category')

    @api.onchange('item')
    def onchange_item(self):
        for note in self:
            note.company_id = False
            note.partner_id = False
            note.partnertag_id = False
            note.product_id = False
            note.productcat_id = False

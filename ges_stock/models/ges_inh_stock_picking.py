# -*- coding: utf-8 -*-

import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('move_line_ids.result_package_id', 'move_line_ids.result_package_id.shipping_weight', 'weight_bulk')
    def _compute_shipping_weight(self):
        for picking in self:
            # if shipping weight is not assigned => default to calculated product weight
            picking.shipping_weight = 0

    @api.onchange('partner_id')
    def _default_copies(self):
        if self.partner_id and self.partner_id.ges_deliv_copies:
            self.ges_copies = self.partner_id.ges_deliv_copies

    def _ges_compute_picker_bool(self):
        for sp in self:
            sp.ges_picker_req = bool(
                self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_picker_bool'))

    @api.depends('move_lines.ges_amount')
    def _ges_compute_amount(self):
        for pick in self:
            pick.ges_amount = sum([m.ges_amount for m in pick.move_lines])

    ges_copies = fields.Integer(
        string="Number of copies", default=_default_copies)
    ges_picker_id = fields.Many2one('ges.picker', string='Picker')
#     ges_picker_bool = fields.Boolean(compute='_ges_compute_picker_bool', store=True)
    ges_picker_req = fields.Boolean(
        compute='_ges_compute_picker_bool', store=True)

    ges_amount = fields.Float(
        "Amount", compute="_ges_compute_amount", store=True)

    ges_pack = fields.Float(string="Total packages",
                            compute='_compute_ges_pack_weight_piece')
    ges_nweight = fields.Float(
        string="Total net weight", compute='_compute_ges_pack_weight_piece', digits=('Product Unit of Measure'))
    ges_gweight = fields.Float(
        string="Total gross weight", compute='_compute_ges_pack_weight_piece', digits=('Product Unit of Measure'))
    ges_piece = fields.Integer(
        string="Total net weight", compute='_compute_ges_pack_weight_piece')

    ges_imp_lot = fields.Selection([('all', 'All'), ('first', 'First')], string="Lot printing method", default=lambda self: self._get_param_lot(), help="""On the report Invoice with lots or delivery slips, print all the lots or only the first with all quantity computed.""")

    def _get_param_lot(self):
        return self.env['ir.config_parameter'].sudo().get_param('ges_base.ges_inv_lot')
#     ges_nbpal = fields.Float(compute='_compute_ges_pack_pal_weight')


#     def button_validate(self):
#         test_val = True
#         if test_val:
#             self = self.with_context(skip_backorder=True)
#         return super(StockPicking, self).button_validate()


    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        for sp in res:
            if sp.ges_copies == 0 or not sp.ges_copies:
                if sp.partner_id:
                    sp.write({'ges_copies': sp.partner_id.ges_deliv_copies})
        return res

    @api.depends('move_lines.ges_pack', 'move_lines.ges_nweight', 'move_lines.ges_gweight', 'move_lines.ges_piece')
    def _compute_ges_pack_weight_piece(self):
        for sp in self:
            wnbcol = sum(
                [move.ges_pack for move in sp.move_lines if move.state != 'cancel'])
            wnbpiece = sum(
                [move.ges_piece for move in sp.move_lines if move.state != 'cancel'])
            wpoin = sum(
                [move.ges_nweight for move in sp.move_lines if move.state != 'cancel'])
            wpoib = sum(
                [move.ges_gweight for move in sp.move_lines if move.state != 'cancel'])
            sp.ges_pack = wnbcol
            sp.ges_piece = wnbpiece
            sp.ges_nweight = wpoin
            sp.ges_gweight = wpoib

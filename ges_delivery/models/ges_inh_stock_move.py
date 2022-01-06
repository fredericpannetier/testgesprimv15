# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    ges_gross_weight = fields.Float(
        compute='_ges_cal_move_line_gross_weight', digits='Stock Weight', store=True, compute_sudo=True)

    @api.depends('product_id', 'product_uom_qty')
    def _ges_cal_move_line_gross_weight(self):
        mls_with_weight = self.filtered(
            lambda mls: mls.product_id.weight > 0.00)
        for ml in mls_with_weight:
            if ml.state == 'done':
                ml.ges_gross_weight = (ml.qty_done * ml.product_id.weight)
            else:
                ml.ges_gross_weight = (
                    ml.product_uom_qty * ml.product_id.weight)
        (self - mls_with_weight).ges_gross_weight = 0

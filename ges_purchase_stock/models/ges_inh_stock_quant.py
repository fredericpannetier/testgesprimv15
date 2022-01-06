# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.depends('company_id', 'location_id', 'owner_id', 'product_id', 'quantity', 'lot_id')
    def _compute_value(self):
        super(StockQuant, self)._compute_value()
        for quant in self:
            if quant.lot_id:
                quant.value = quant.quantity * quant.lot_id.ges_purchase_price

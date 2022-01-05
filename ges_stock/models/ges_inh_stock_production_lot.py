# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import ceil
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.tools import float_utils


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    ges_suppbatch = fields.Char("Supplier lot", readonly=True)
    ges_available = fields.Char("Lot available", compute="_compute_available", store=True)

    @api.depends("product_id.qty_available")
    def _compute_available(self):
        for lot in self:
            if lot.product_id.qty_available > 0:
                lot.ges_available = 'yes'
            else:
                lot.ges_available = 'no'

    def ges_update_suppbatch(self):
        for lot in self:
            lot.ges_suppbatch = ''
            lst_lot = []
            ml_inc = self.env['stock.move.line'].search([('picking_id', '!=', False), ('lot_id', '=', lot.id)]).filtered(
                lambda ml: ml.location_id.usage != 'customer' and ml.picking_id.picking_type_id.code == 'incoming')
            for ml in ml_inc:
                if ml.ges_suppbatch:
                    lst_lot.append(ml.ges_suppbatch)
            lst_lot = list(set(lst_lot))
            for elem in lst_lot:
                lot.ges_suppbatch = lot.ges_suppbatch+str(elem)+';'

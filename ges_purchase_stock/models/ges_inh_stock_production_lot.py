# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import ceil
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.tools import float_utils


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    purchase_order_ids = fields.Many2many('purchase.order', string="Purchase Orders", compute='_compute_purchase_order_ids', readonly=True, store=True)
    # obligé de mettre ce champ en store = True car sinon on ne peut pas l'utiliser dans le depends  de ges_purchase_price (sauvegarde super lente)
    ges_purchase_price = fields.Float(string="Purchase price", digits="Product Price",
                                      compute='_compute_ges_purchase_price', readonly=True, store=True)

    @api.depends('purchase_order_ids.order_line.price_unit', 'purchase_order_ids.order_line.product_qty')
    def _compute_ges_purchase_price(self):
        for lot in self:
            stock_moves = self.env['stock.move.line'].search([
                ('lot_id', '=', lot.id),
                ('state', '=', 'done')
            ]).mapped('move_id')
            stock_moves = stock_moves.search([('id', 'in', stock_moves.ids)]).filtered(
                lambda move: move.picking_id.location_id.usage == 'supplier' and move.state == 'done')
            amount = 0.0
            qty = 0.0
            for move in stock_moves:
                if move.purchase_line_id:
                    amount += (move.purchase_line_id.product_qty *
                               move.purchase_line_id.price_unit)
                    qty += move.purchase_line_id.product_qty
            if qty == 0:
                qty = 1
            lot.ges_purchase_price = amount / qty

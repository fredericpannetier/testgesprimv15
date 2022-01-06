# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('move_ids', 'move_ids.move_line_ids', 'move_ids.move_line_ids.lot_id', 'move_ids.move_line_ids.lot_id.ges_purchase_price')
    def _compute_purchase_price(self):
        lines_without_price_on_lot = self.browse()
        for line in self:
            if not line.move_ids:
                lines_without_price_on_lot |= line
            else:
                amount = 0.0
                qty = 0.0
                for move in line.move_ids:
                    for ml in move.move_line_ids:
                        if ml.lot_id:
                            if ml.state == 'done':
                                amount += ml.lot_id.ges_purchase_price * ml.qty_done
                                qty += ml.qty_done
                            else:
                                amount += ml.lot_id.ges_purchase_price * ml.product_uom_qty
                                qty += ml.product_uom_qty
                if qty == 0:
                    qty = 1

                line.purchase_price = amount / qty
                if line.purchase_price == 0:
                    lines_without_price_on_lot |= line

        return super(SaleOrderLine, lines_without_price_on_lot)._compute_purchase_price()

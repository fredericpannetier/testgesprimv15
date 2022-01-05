# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import ceil
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.tools import float_utils


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `product_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        super(StockMove, self)._action_assign()
        for move in self:
            for line in move.move_line_ids:
                line.qty_done = line.product_uom_qty

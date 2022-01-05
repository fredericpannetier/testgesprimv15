# -*- coding: utf-8 -*-

import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        self = self.with_context(
            skip_backorder=True, picking_ids_not_to_backorder=self.ids)
        return super(StockPicking, self).button_validate()

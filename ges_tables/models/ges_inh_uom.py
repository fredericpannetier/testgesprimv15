# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class UoM(models.Model):
    _inherit = "uom.uom"

    ges_unittype = fields.Selection(string="Unit type", selection=[('Piece', 'Piece'), ('Package', 'Package'), ('Net weight', 'Net weight'), ('Misc.', 'Misc.')],
                                    help="""Allow to calculate packages quantity""", required=True, default=lambda self: self._get_default_value())

    @api.onchange('category_id')
    def ges_onchange_categ(self):
        if self.category_id.name == 'Unit':
            self.ges_unittype = 'Piece'
        elif self.category_id.name == 'Weight':
            self.ges_unittype = 'Net weight'
        else:
            self.ges_unittype = 'Misc.'

    def _get_default_value(self):
        if self.category_id.name == 'Unit':
            retour = 'Piece'
        elif self.category_id.name == 'Weight':
            retour = 'Net weight'
        else:
            retour = 'Misc.'

        return retour

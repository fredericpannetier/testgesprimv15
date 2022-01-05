
# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("siret", "country_id")
    def _onchange_siret(self):
        if self.siret and self.country_id.code:
            siren = self.siret[0:9]
            vatkey = str((12+(3*(int(siren) % 97))) % 97)
            self.vat = self.country_id.code+vatkey+siren

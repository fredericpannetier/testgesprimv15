# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class GesBrand(models.Model):
    _name = "ges.brand"
    _description = "Brand"
    _order = "name"

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,  default=lambda self: self.env.user.company_id)
    des = fields.Char(string="Description", required=True)
    name = fields.Char(string="Code", required=True)

    @api.constrains('name')
    def _check_name(self):
        for tab in self:
            if tab.name:
                name = tab.search([
                    ('id', '!=', tab.id),
                    ('name', '=', tab.name)], limit=1)
                if name:
                    raise ValidationError(_("Code is already used"))

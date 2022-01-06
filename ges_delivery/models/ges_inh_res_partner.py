
# -*- coding: utf-8 -*-
from odoo.tools.misc import ustr
from odoo.exceptions import Warning
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    ges_ship_cost_owed = fields.Boolean(string="Shipping cost owed", default=True,
                                        help="If this box is not checked, the customer will not have to pay the shipping cost.")
#     ges_carrier_id = fields.Many2one('delivery.carrier', string="Delivery Method", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

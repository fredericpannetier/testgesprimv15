
# -*- coding: utf-8 -*-
from odoo.tools.misc import ustr
from odoo.exceptions import Warning
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    ges_val_deliv = fields.Boolean(string="Valuated delivery note", default=False,
                                   help="Check if the delivery note must be valuated")
    ges_order_copies = fields.Integer(
        string="Order number of copies", default=1)
    ges_deliv_copies = fields.Integer(
        string="Delivery number of copies", default=1)
    ges_inv_copies = fields.Integer(
        string="Invoice number of copies", default=1)
    ges_tour = fields.Char(string='Tour', help="""Tour""")
    ges_ranktour = fields.Char(string='Rank in Tour', help="""Rank in Tour""")
    ges_deliverydelay = fields.Integer(string="Delivery delay", help="""Default preparation delay between preparation date and delivery date""")

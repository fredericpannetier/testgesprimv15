# -*- coding: utf-8 -*-

import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('name')
    def _compute_tour(self):
        for sp in self:
            # pour éviter erreur de tri à l'édition du bordereau de transport
            sp.ges_tour = sp.sale_id.ges_tour
            sp.ges_ranktour = sp.sale_id.ges_ranktour
#             so = self.env['sale.order'].browse(sp.sale_id.id)
#             if sp.origin and sp.origin != '' and sp.origin!="New":
#                 so = self.env['sale.order'].search([('name', '=', sp.origin)])

#             if so:
#                 if so.ges_tour:
#                     sp.ges_tour = so.ges_tour
#                 if so.ges_ranktour:
#                     sp.ges_ranktour = so.ges_ranktour

    ges_tour = fields.Char(string="Tour", compute='_compute_tour', store=True)
    ges_ranktour = fields.Char(
        string="Rank in tour", compute='_compute_tour', store=True)

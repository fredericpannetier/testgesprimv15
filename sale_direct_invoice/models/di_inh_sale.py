
# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
from functools import partial
from odoo.tools.misc import formatLang, get_lang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def di_action_invoice(self, confirm_invoice):
        for order in self:
            if order.state in ('draft', 'sent'):
                order.action_confirm()
            if order.state in ('draft', 'sent', 'sale'):
                livraisons = order.mapped('picking_ids')
                for livraison in livraisons:
                    if livraison.state == 'confirmed':
                        livraison.action_assign()
                    if livraison.state == 'assigned':
                        livraison.button_validate()
                        if livraison.state == 'done':
                            order._create_invoices()
                            invoice = order.mapped('invoice_ids')
                            if confirm_invoice:
                                invoice.action_post()

        return self

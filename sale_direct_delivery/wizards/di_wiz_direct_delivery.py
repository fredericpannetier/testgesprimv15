# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class DiDirectDeliveryWiz(models.TransientModel):
    _name = "di.direct.delivery.wiz"
    _description = "Confirm quotations assign products and validate deliveries"

    def di_massive_order_confirm(self):
        order_ids = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        ok = True
        orders_to_deliver = order_ids.filtered(lambda o: o.state in ('draft', 'sent'))
        orders_to_deliver.di_action_order_confirm()
        for order in orders_to_deliver:
            if order.state != 'sale':
                ok = False
                break
        if not ok:
            return self.env['di.wiz.popup'].show_message(_("Warning ! Some of the orders have not been confirmed."), True, False, False, False)
        else:
            return self.env['di.wiz.popup'].show_message(_("Process completed."), True, False, False, False)

    def di_massive_deliveries(self):
        order_ids = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        ok = True
        orders_to_deliver1 = order_ids.filtered(lambda o: o.state in ('draft', 'sent'))
        orders_to_deliver1.di_action_deliver()
        orders_to_deliver2 = order_ids.filtered(lambda o: o.state == 'sale')
        orders_to_deliver2.di_action_deliver()
        orders_to_deliver = orders_to_deliver1 + orders_to_deliver2
        for order in orders_to_deliver:
            deliveries = order.mapped('picking_ids')
            for delivery in deliveries:
                if delivery.state != 'done':
                    ok = False
                    break
        if not ok:
            return self.env['di.wiz.popup'].show_message(_("Warning ! Some of the deliveries have not been validated due to a lack of stock."), True, False, False, False)
        else:
            return self.env['di.wiz.popup'].show_message(_("Process completed."), True, False, False, False)

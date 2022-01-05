
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class DiDirectInvoiceWiz(models.TransientModel):
    _name = "di.direct.invoice.wiz"
    _description = "Confirm quotations assign products and validate invoices"

    confirm_invoice = fields.Boolean("Confirm invoice", default=False)

    def di_massive_invoices(self):
        order_ids = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        ok = True
        # orders_to_invoice = order_ids.filtered(lambda o: o.state in ('draft', 'sent'))
        # orders_to_invoice.di_action_invoice(self.confirm_invoice)

        orders_to_invoice1 = order_ids.filtered(lambda o: o.state in ('draft', 'sent'))
        orders_to_invoice1.di_action_invoice(self.confirm_invoice)
        orders_to_invoice2 = order_ids.filtered(lambda o: o.state == 'sale')
        orders_to_invoice2.di_action_invoice(self.confirm_invoice)
        orders_to_invoice = orders_to_invoice1 + orders_to_invoice2

        for order in orders_to_invoice:
            if order.invoice_status != 'invoiced':
                ok = False
                break
        if not ok:
            return self.env['di.wiz.popup'].show_message(_("Warning ! Some of the orders have not been invoiced. Please check the concerned orders."), True, False, False, False)
        else:
            return orders_to_invoice.action_view_invoice()
#             return self.env['di.wiz.popup'].show_message(_("Process completed."),True,False,False,False)

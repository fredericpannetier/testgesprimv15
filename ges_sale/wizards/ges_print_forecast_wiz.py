# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class GesPrintForecastWiz(models.TransientModel):
    _name = "ges.print.forecast.wiz"
    _description = "Print forecast"

    def _default_date_init(self):
        return datetime.today().date()

    product_ids = fields.Many2many(
        "product.product", string="Products to print")
    draft = fields.Boolean("Count draft orders", default=True)
    po = fields.Boolean("Incoming", default=True)
    so = fields.Boolean("Outgoing", default=True)
    only_missing = fields.Boolean(
        "Only missing", help="Show only missing products", default=False)
    from_date = fields.Date("From", default=False)
    to_date = fields.Date("To", default=False)

    def print_forecast(self):
        domain = [('type', '=', 'product')]
#         if self.only_missing:
#             domain=[('virtual_available','<',0)]
        self.product_ids = self.env['product.product'].search(
            domain)  # .with_context(ges_draft=self.draft)
#         self.product_ids.env.context.update(ges_draft=self.draft)

        return self.env.ref('ges_sale.ges_action_report_forecast').report_action(self)

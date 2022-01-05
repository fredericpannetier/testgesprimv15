# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from math import ceil


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "order_id.partner_id")
    def _compute_last_prices(self):
        for sol in self:
            if (sol.product_id and sol.order_id.partner_id
               and sol.order_id.date_order):
                last_prices = _("""
                <table class="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Quantity</th>
                            <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                """)
                query = """ select so.date_order, sol.product_uom_qty,
                                    sol.price_unit
                                    from sale_order_line sol
                                    left join sale_order so
                                    on so.id = sol.order_id
                                    where sol.product_id  =  %(product_id)s
                                    and so.partner_id  =  %(partner_id)s
                                    and so.date_order  <  %(date)s
                                    and sol.price_unit <> 0
                                    and sol.product_uom_qty <> 0
                                    order by so.date_order desc , sol.id
                                    limit 5
                                """
                query_args = {'product_id': sol.product_id.id,
                              'partner_id': sol.order_id.partner_id.id,
                              'date': sol.order_id.date_order}

                self.env.cr.execute(query, query_args)
                for r in self.env.cr.fetchall():
                    last_prices = last_prices + \
                        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                            r[0], r[1], r[2])

                last_prices = last_prices+"""
                    </tbody>
                </table>"""
                self.di_table_last_prices = last_prices
            else:
                self.di_table_last_prices = ""

    di_table_last_prices = fields.Html(
        string="Last prices", compute="_compute_last_prices")

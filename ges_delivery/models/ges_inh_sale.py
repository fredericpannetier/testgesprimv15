# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from math import ceil


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def _ges_onchange_partner(self):
        if self.partner_id:
            self.carrier_id = self.partner_id.property_delivery_carrier_id
            if self.carrier_id:
                self.recompute_delivery_price = True
            else:
                self.recompute_delivery_price = False
        else:
            self.carrier_id = False
            self.recompute_delivery_price = False

    @api.onchange('partner_id')
    def _ges_tour_onchange(self):
        if self.partner_id and self.partner_id.ges_tour:
            self.ges_tour = self.partner_id.ges_tour

    @api.onchange('partner_id')
    def _ges_ranktour_onchange(self):
        if self.partner_id and self.partner_id.ges_ranktour:
            self.ges_ranktour = self.partner_id.ges_ranktour

    def _default_Tour(self):
        if self.partner_id and self.partner_id.ges_tour:
            self.ges_tour = self.partner_id.ges_tour

    def _default_Ranktour(self):
        if self.partner_id and self.partner_id.ges_ranktour:
            self.ges_ranktour = self.partner_id.ges_ranktour

    @api.depends('order_line.price_unit')
    def _ges_compute_delivery_price(self):
        for order in self:
            order.ges_delivery_price = sum(
                [line.price_subtotal for line in order.order_line if line.is_delivery])

#     def write(self, vals):
#         res = super(SaleOrder, self).write(vals)
#         lines = False
#         for order in self:    #
#             #ajout ligne transport
#             if order.carrier_id and order.state in ("draft","sent") and order.recompute_delivery_price:
#                 cdc = self.env['choose.delivery.carrier'].create({
#                     'order_id':order.id,
#                     'carrier_id':order.carrier_id.id,
#                     })
#                 if cdc._get_shipment_rate() == {}:
#                     order.set_delivery_line(cdc.carrier_id, cdc.delivery_price)
#                     order.recompute_delivery_price = False
# #                     order.delivery_message = self.delivery_message
#         return res

    def set_delivery_line(self, carrier, amount):
        super(SaleOrder, self).set_delivery_line(carrier, amount)
        if not amount or amount == 0:
            # Remove delivery products from the sales order
            self._remove_delivery_line()
        for order in self:
            order.carrier_id = carrier.id
        return True

    @api.model
    def create(self, vals):

        cde = super(SaleOrder, self).create(vals)

        for order in cde:
            #             #ajout ligne transport
            if order.carrier_id and order.state in ("draft", "sent") and order.recompute_delivery_price:
                cdc = self.env['choose.delivery.carrier'].create({
                    'order_id': order.id,
                    'carrier_id': order.carrier_id.id,
                })
                if cdc._get_shipment_rate() == {}:
                    order.set_delivery_line(cdc.carrier_id, cdc.delivery_price)
                    order.recompute_delivery_price = False
        return cde

    def ges_recompute_shipping(self):
        for order in self:
            if order.carrier_id and order.recompute_delivery_price and order.state in ("draft", "sent"):
                cdc = self.env['choose.delivery.carrier'].create({
                    'order_id': order.id,
                    'carrier_id': order.carrier_id.id,
                })
                if cdc._get_shipment_rate() == {}:
                    order.set_delivery_line(cdc.carrier_id, cdc.delivery_price)
                    order.recompute_delivery_price = False
                    order.delivery_message = self.delivery_message
#                     order.write({
#                         'recompute_delivery_price': False,
#                         'delivery_message': self.delivery_message,
#                     })
                    # self.env.cr.commit()

    ges_tour = fields.Char(
        string='Tour', help="""Tour""", default=_default_Tour)
    ges_ranktour = fields.Char(
        string='Rank in Tour', help="""Rank in Tour""", default=_default_Ranktour)
    ges_delivery_price = fields.Float(
        string='Estimated Delivery Price', compute="_ges_compute_delivery_price")

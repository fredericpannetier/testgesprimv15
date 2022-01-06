# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ChooseDeliveryCarrier(models.TransientModel):    
    _inherit = 'choose.delivery.carrier'    
    
#     @api.onchange('carrier_id')
#     def _onchange_carrier_id(self):
#         ret = super(ChooseDeliveryCarrier, self)._onchange_carrier_id()
#         if not ret.get('error'):
#             if not self.ges_ship_cost_owed:
#                 self.delivery_price = 0
#         return ret
#             
#         self.delivery_message = False
#         if self.delivery_type in ('fixed', 'base_on_rule'):
#             vals = self._get_shipment_rate()
#             if vals.get('error_message'):
#                 return {'error': vals['error_message']}
#         else:
#             self.display_price = 0
#             self.delivery_price = 0
            
            
    def _get_shipment_rate(self):        
        ret = super(ChooseDeliveryCarrier, self)._get_shipment_rate()
        if ret == {}:
            if not self.ges_ship_cost_owed:
                self.delivery_price = 0
                self.display_price = 0
        return ret
    
    
    @api.depends('ges_ship_cost_owed')
    def _ges_compute_ship_cost_message(self):
        for wiz in self:
            if not wiz.ges_ship_cost_owed :
                wiz.ges_ship_cost_message = _("Warning ! The shipping cost is not owed by the customer. The shipping cost will be set to 0.")
            else:
                wiz.ges_ship_cost_message = ""
    
    ges_ship_cost_owed = fields.Boolean(related='partner_id.ges_ship_cost_owed')
    ges_ship_cost_message = fields.Text(readonly=True, compute="_ges_compute_ship_cost_message")    
   
    def button_confirm(self):
        if not self.ges_ship_cost_owed:
            self.order_id.set_delivery_line(self.carrier_id, 0)
        else:
            self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
        self.order_id.write({
            'recompute_delivery_price': False,
            'delivery_message': self.delivery_message,
        })

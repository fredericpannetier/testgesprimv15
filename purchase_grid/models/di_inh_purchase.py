# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def di_purchasegrid_action(self):
        self.ensure_one()

        view = self.env.ref('purchase_grid.di_grid_purchase_wiz').id
        #

        ctx = {
            'di_model': 'purchase.order',
            'di_order': self
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': 'Purchase Grid',
            'res_model': 'di.purchase.grid.wiz',
            'views': [(view, 'form')],
            'view_id': view,
            'target': 'new',
            'id': 'di_purchase_grid_action_wiz',
            'key2': 'client_action_multi',
            'context': ctx
        }

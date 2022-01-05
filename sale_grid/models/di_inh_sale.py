# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def di_salegrid_action(self):
        self.ensure_one()
        view = self.env.ref('sale_grid.di_grid_sale_wiz').id
        ctx = {
            'di_model': 'sale.order',
            'di_order': self
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': 'Sale Grid',
            'res_model': 'di.sale.grid.wiz',
            'views': [(view, 'form')],
            'view_id': view,
            'target': 'new',
            'multi': 'False',
            'id': 'di_sale_grid_action_wiz',
            'key2': 'client_action_multi',
            'context': ctx
        }

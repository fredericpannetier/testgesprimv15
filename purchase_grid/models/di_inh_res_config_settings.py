# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    di_purch_horizon = fields.Integer(string="Purchase grid horizon", help="""Sale grid horizon in days """,
                                      config_parameter="purchase_grid.di_purch_horizon")
    di_purch_grid_mode = fields.Selection(string="Purchase grid type", selection=[('Horizon', 'Horizon'),
                                                                                  ('Order Number', 'Order Number')], default='Horizon',
                                          help="""Search type for purchase grid""",
                                          config_parameter="purchase_grid.di_purch_grid_mode")
    di_purch_order_num = fields.Integer(string="Purchase order number", help="""Purchase grid horizon in order number """,
                                        config_parameter="purchase_grid.di_purch_order_num")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'purchase_grid.di_purch_horizon', self.di_purch_horizon)
        self.env['ir.config_parameter'].set_param(
            'purchase_grid.di_purch_grid_mode', self.di_purch_grid_mode)
        self.env['ir.config_parameter'].set_param(
            'purchase_grid.di_purch_order_num', self.di_purch_order_num)

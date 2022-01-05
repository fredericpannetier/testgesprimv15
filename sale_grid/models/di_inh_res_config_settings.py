# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    di_sale_horizon = fields.Integer(string="Sale grid horizon", help="""Sale grid horizon in days """,
                                     config_parameter="sale_grid.di_sale_horizon")
    di_sale_grid_mode = fields.Selection(string="Sale grid type", selection=[('Horizon', 'Horizon'),
                                                                             ('Order Number', 'Order Number')], default='Horizon',
                                         help="""Search type for sale grid""",
                                         config_parameter="sale_grid.di_sale_grid_mode")
    di_sale_order_num = fields.Integer(string="Sale order number", help="""Sale grid horizon in order number """,
                                       config_parameter="sale_grid.di_sale_order_num")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'sale_grid.di_sale_horizon', self.di_sale_horizon)
        self.env['ir.config_parameter'].set_param(
            'sale_grid.di_sale_grid_mode', self.di_sale_grid_mode)
        self.env['ir.config_parameter'].set_param(
            'sale_grid.di_sale_order_num', self.di_sale_order_num)

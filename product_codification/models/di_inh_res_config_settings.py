# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    di_prod_seq = fields.Boolean(string="Product automatic codification",
                                 help="""If true, you can leave the default code empty. Then the program will generate a default code.""", config_parameter='product_codification.di_prod_seq')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'product_codification.di_prod_seq', self.di_prod_seq)

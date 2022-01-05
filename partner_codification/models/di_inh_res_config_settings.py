# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    di_cus_seq = fields.Boolean(string="Customer automatic codification",
                                help="""If true, you can leave the ref empty. Then the program will generate a ref.""", config_parameter='partner_codification.di_cus_seq')
    di_sup_seq = fields.Boolean(string="Supplier automatic codification",
                                help="""If true, you can leave the ref empty. Then the program will generate a ref.""", config_parameter='partner_codification.di_sup_seq')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'partner_codification.di_cus_seq', self.di_cus_seq)
        self.env['ir.config_parameter'].set_param(
            'partner_codification.di_sup_seq', self.di_sup_seq)

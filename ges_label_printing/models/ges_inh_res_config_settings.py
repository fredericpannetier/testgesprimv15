# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ges_default_label_printer = fields.Many2one('di.printing.printer', string='Default label printer',
                                                help="Default label printer", config_parameter='ges_base.ges_default_label_printer')
    ges_default_label_model = fields.Many2one('di.printing.etiqmodel', string='Default label model',
                                              help="Default label model", config_parameter='ges_base.ges_default_label_model')

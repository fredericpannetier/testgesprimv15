# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    di_gen_lot = fields.Selection([('none', 'None'), ('seq', 'Sequence'), ('po', 'Order #')], default='none', help="""The lot may by 
    automatically created. 
    If Sequence is choosen then it will be calculated with the selected sequence. 
    If Order # is choosen then the lot will be equal to the purchase order number or the picking number if there is no order.""",
                                  config_parameter='purchase_auto_batch.di_gen_lot')
    di_seq_lot = fields.Many2one(
        "ir.sequence", string="Lot sequence", config_parameter='purchase_auto_batch.di_seq_lot')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'purchase_auto_batch.di_gen_lot', self.di_gen_lot)

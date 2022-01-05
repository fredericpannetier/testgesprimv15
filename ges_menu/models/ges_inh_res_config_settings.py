# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _domain_location_id(self):
        return [('usage', '=', 'inventory')]

    ges_marg_mini = fields.Integer(string="Minimal Margin ratio", help="""Minimal Margin ratio to control on sale orders """,
                                   config_parameter="ges_base.ges_marg_mini")
    ges_prepdelay = fields.Integer(string="Default preparation delay", help="""Default preparation delay between entry date and preparation date""",
                                   config_parameter="ges_base.ges_prepdelay")
    ges_deliverydelay = fields.Integer(string="Default delivery delay", help="""Default preparation delay between preparation date and delivery date""",
                                       config_parameter="ges_base.ges_deliverydelay")
    ges_picker_bool = fields.Boolean(string="Picker Required", help="""Picker Required on delivery orders""",
                                     config_parameter="ges_base.ges_picker_bool", default=False)
    ges_loss_location = fields.Many2one('stock.location', 'Loss location', domain=lambda self: self._domain_location_id(
    ), config_parameter='ges_base.ges_loss_location')
    ges_dest_location = fields.Many2one('stock.location', 'Destruction location', domain=lambda self: self._domain_location_id(
    ), config_parameter='ges_base.ges_dest_location')

    ges_purch_pricelist = fields.Many2one('product.pricelist', 'Purchase pricelist', config_parameter='ges_base.ges_purch_pricelist')
    ges_pp_pricelist = fields.Many2one('product.pricelist', 'Sale pricelist', config_parameter='ges_base.ges_pp_pricelist')

    ges_inv_lot = fields.Selection([('all', 'All'), ('first', 'First')], string="Lot printing method", default='all', help="""On the report Invoice with lots or delivery slips, print all the lots or only the first with all quantity computed.""",
                                   config_parameter='ges_base.ges_inv_lot')

    group_manage_pal = fields.Boolean(
        "Manage pallets", implied_group='ges_menu.group_manage_pal')

    group_simple_pal = fields.Boolean("Simple palletization", implied_group='ges_menu.group_simple_pal',
                                      default=True, help="""If not checked, it will show advanced functionalities for palletization """)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'ges_base.ges_marg_mini', self.ges_marg_mini)
        self.env['ir.config_parameter'].set_param(
            'ges_base.ges_prepdelay', self.ges_prepdelay)
        self.env['ir.config_parameter'].set_param(
            'ges_base.ges_deliverydelay', self.ges_deliverydelay)
        self.env['ir.config_parameter'].set_param(
            'ges_base.ges_picker_bool', self.ges_picker_bool)
        self.env['ir.config_parameter'].set_param(
            'ges_base.ges_inv_lot', self.ges_inv_lot)

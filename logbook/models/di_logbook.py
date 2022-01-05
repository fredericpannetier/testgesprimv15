# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
import datetime


class DiLogBook(models.Model):
    _name = "di.logbook"
    _description = "LogBook"
    _order = "name"

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,  default=lambda self: self.env.user.company_id)
    name = fields.Char(string="Code", default=lambda self: self.env.user.name +
                       (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    message = fields.Char(string="Message", required=True)

    def record_to_logbook(self, mess):
        """
        Method to use to record message on logbook
        user this following commands
        lb = self.env['di.logbook']
        lb.record_to_logbook("Test message")
        """
        self.env['di.logbook'].create({'message': mess})

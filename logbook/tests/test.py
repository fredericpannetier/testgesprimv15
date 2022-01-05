# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from odoo.tests import TransactionCase

class DiTestLogBook(TransactionCase):
    def test_some_action(self):
        lb = self.env['di.logbook']
        TxtMessage  = "Test message"
        lb.record_to_logbook(TxtMessage)
        id  = lb.id
        lb2 = self.env['di.logbook'].browse(id)
        self.assertEqual(lb2.message,TxtMessage)
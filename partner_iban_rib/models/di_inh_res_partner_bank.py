
# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.addons.base_iban.models.res_partner_bank import validate_iban


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

#     acc_type = fields.Selection(selection=lambda x: x.env['res.partner.bank'].get_supported_account_types(), string='Type', help='Bank account type: Normal or IBAN. Inferred from the bank account number.')
    di_ibanctry = fields.Char(string='Country code', help="Country code ")
    di_ibankey = fields.Char(string='Iban key', help="Iban key ")
    di_ibanbk = fields.Char(string='Bank code', help="Bank code ")
    di_ibanbksortcode = fields.Char(
        string='Bank sort code', help="Bank sort code ")
    di_ibanacc = fields.Char(string='Account', help="Account ")
    di_ibanribkey = fields.Char(string='RIB key', help="RIB key ")
    acc_number = fields.Char(
        'Account Number', required=True, store=True, compute="_di_compute_iban")

    @api.depends('di_ibanctry', 'di_ibankey', 'di_ibanbk', 'di_ibanbksortcode', 'di_ibanacc', 'di_ibanribkey')
    def _di_compute_iban(self):
        #         self.acc_number = self.di_ibanctry and self.di_ibanctry or ''+self.di_ibankey and self.di_ibankey or ''+self.di_ibanbk and self.di_ibanbk or ''
        #         +self.di_ibanbksortcode and self.di_ibanbksortcode or ''+self.di_ibanacc and self.di_ibanacc or ''+self.di_ibanribkey and self.di_ibanribkey or ''
        #         self.acc_number = str(self.di_ibanctry) +str(self.di_ibankey)+str(self.di_ibanbk)+str(self.di_ibanbksortcode) +str(self.di_ibanacc) +str(self.di_ibanribkey)
        #         self.acc_number = str(self.di_ibanctry and self.di_ibanctry or '') +str(self.di_ibankey and self.di_ibankey or '')+str(self.di_ibanbk and self.di_ibanbk or '')
        #         +str(self.di_ibanbksortcode and self.di_ibanbksortcode or '') +str(self.di_ibanacc and self.di_ibanacc or '') +str(self.di_ibanribkey and self.di_ibanribkey or '')
        self.acc_number = ''
        if self.di_ibanctry:
            self.acc_number = self.acc_number+self.di_ibanctry
        if self.di_ibankey:
            self.acc_number = self.acc_number+self.di_ibankey
        if self.di_ibanbk:
            self.acc_number = self.acc_number+self.di_ibanbk
        if self.di_ibanbksortcode:
            self.acc_number = self.acc_number+self.di_ibanbksortcode
        if self.di_ibanacc:
            self.acc_number = self.acc_number+self.di_ibanacc
        if self.di_ibanribkey:
            self.acc_number = self.acc_number+self.di_ibanribkey

    @api.constrains('acc_number')
    def _check_iban(self):
        for bank in self:
            #             if bank.acc_type == 'iban':
            validate_iban(bank.acc_number)
#     @api.constrains('acc_type')
#     def _check_acc_type(self):
#         for acc in self:
#             if acc.acc_type:
#                 if acc.acc_type != 'iban':
#                     raise ValidationError(_("The account number is not a working IBAN"))
# #

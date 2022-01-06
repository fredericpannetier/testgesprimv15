# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

import calendar
import datetime


class PrintJnl(models.TransientModel):
    _name = 'ges.print.journal.wiz'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    ges_journal = fields.Many2many(
        'account.journal', string="Journals", help="""Journals""", digits=(12, 2), store=True)
    ges_dateB = fields.Date(string="Begining date")
    ges_dateE = fields.Date(string="End date")
    account_move_ids = fields.Many2many(
        'account.move', string='Account Journal')
    tax_group_ids = fields.Many2many(
        'account.tax.group', compute='_compute_taxes_label')        
    currency_symbol = fields.Char(string='Currency', related='company_id.currency_id.symbol')

    @api.depends('account_move_ids')
    def _compute_taxes_label(self):

        lstlabel = []
        for move in self.account_move_ids:
            for group in move.amount_by_group:
                if group[6] not in lstlabel:
                    lstlabel.append(group[6])

        if lstlabel:
            #                 taxes_label=taxes_label+'<th><h5 style="text-align: center">%s</h5></th>' % label
            self.tax_group_ids = [(6, 0, lstlabel)]

    def edit_journal(self):
        # on récupère les livraisons du jour
        #         wdate       = self.date_sel
        #         date_deb    = datetime.datetime(wdate.year,wdate.month,wdate.day,0,0,0,0).strftime("%Y-%m-%d %H:%M:%S")
        #         date_fin    = datetime.datetime(wdate.year,wdate.month,wdate.day,23,59,59,0).strftime("%Y-%m-%d %H:%M:%S")
        self.account_move_ids = self.env['account.move'].search(
            ['&', '&', '&', ('date', '>', self.ges_dateB), ('date', '<', self.ges_dateE), ('state', '=', 'posted'), ('company_id', '=', self.company_id.id)])

        if self.account_move_ids:
            return self.env.ref('ges_sales_purchases.ges_wiz_report_journal').report_action(self)
        return {}

    @api.model
    def default_get(self, fields):
        res = super(PrintJnl, self).default_get(fields)
        today = datetime.date.today()
        res['ges_dateB'] = today.replace(day=1)
        res['ges_dateE'] = datetime.date(
            today.year, today.month, calendar.monthrange(today.year, today.month)[-1])
        journal_type = self.env.context.get('journal_type')
        journals = self.env['account.journal']
        if journal_type == 'sale':
            journals = journals.search([('type', '=', 'sale')])
        else:
            journals = journals.search([('type', '=', 'purchase')])

        if journals:
            res['ges_journal'] = [(6, 0, journals.ids)]

        return res

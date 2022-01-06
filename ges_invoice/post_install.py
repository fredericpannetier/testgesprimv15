# Copyright 2016-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def create_interfel(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
#         atg = env["account.tax.group"]
#         atg.create({'name':'Interfel'})
        
        
        at = env["account.tax"]
        
        at.create({
            'description':'Interfel',
            'type_tax_use':'sale',
            'name':'Interfel',
            'amount_type':'percent',
            'amount': 0.206,
            'tax_group_id':env.ref("ges_invoice.ges_tax_group_tva_interfel").id,#env["account.tax.group"].create({'name':'Interfel'}).id,
            'di_tax_id':env.ref("l10n_fr.tva_normale").id,
            'invoice_repartition_line_ids':[(5, 0, 0),
                    (0,0, {                        
                        'factor_percent': 100,
                        'repartition_type': 'base',
#                         'plus_report_line_ids': [env.ref('l10n_fr.tax_report_01').id, env.ref('l10n_fr.tax_report_08_base').id],
                    }),
        
                    (0,0, {
                        'company_id':env.ref('base.main_company').id,
                        'factor_percent': 100,
                        'repartition_type': 'tax',
#                         'plus_report_line_ids': [env.ref('l10n_fr.tax_report_08_taxe').id],
                        'account_id': env.ref('l10n_fr.pcg_44571').id,
                    }),
                ],
            'refund_repartition_line_ids':[(5, 0, 0),
                    (0,0, {
                        'factor_percent': 100,
                        'repartition_type': 'base',
#                         'minus_report_line_ids': [env.ref('l10n_fr.tax_report_01').id, env.ref('l10n_fr.tax_report_08_base').id],
                    }),
        
                    (0,0, {
                        'company_id':env.ref('base.main_company').id,
                        'factor_percent': 100,
                        'repartition_type': 'tax',
#                         'minus_report_line_ids': [env.ref('l10n_fr.tax_report_08_taxe').id],
                        'account_id': env.ref('l10n_fr.pcg_44571').id,
                    }),
                ],
            })        
    return

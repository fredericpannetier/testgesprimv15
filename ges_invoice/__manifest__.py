# -*- coding: utf-8 -*-
{
    'name': "ges_invoice",

    'summary': """
        ges_invoice""",

    'description': """
        ges_invoice
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'gesprim',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'ges_menu',
        'account', 
        'ges_tables',                 
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [
        "data/ges_groups.xml",
        "data/ges_default_settings.xml",
        "security/ir.model.access.csv",
        "views/ges_inh_account_move_views.xml",
        "reports/ges_inh_invoice_reports.xml",
        "reports/ges_invoice_stat.xml",   
        "menu/ges_menu.xml",      
                                                   
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    "post_init_hook": "create_interfel",
    'installable': True,
    'application': False,
    'auto_install': False,
}
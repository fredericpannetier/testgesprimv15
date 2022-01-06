# -*- coding: utf-8 -*-
{
    'name': "ges_purchase",

    'summary': """
        ges_purchase""",

    'description': """
        ges_purchase
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
        'purchase',                  
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [
        "data/ges_groups.xml",
        "views/ges_inh_purchase_views.xml",
        "reports/ges_purchase_stat.xml",
        "reports/ges_inh_purchase_reports.xml",        
        "menu/ges_menu.xml",        
                                                    
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# -*- coding: utf-8 -*-
{
    'name': "ges_sales_purchases",

    'summary': """
        ges_sales_purchases""",

    'description': """
        ges_sales_purchases
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
          'sale',
          'product',
          'purchase',
        'ges_sale',
        'ges_purchase',
                          
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [                             
        "security/ir.model.access.csv",   
        "wizards/ges_print_journal.xml",
        "views/ges_inh_pricelists.xml",
        "menu/ges_menu.xml",
        "reports/ges_journal.xml",
                             
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
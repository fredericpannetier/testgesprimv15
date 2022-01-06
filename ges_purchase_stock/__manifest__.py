# -*- coding: utf-8 -*-
{
    'name': "ges_purchase_stock",

    'summary': """
        ges_purchase_stock""",

    'description': """
        ges_purchase_stock
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
          'stock',
          'purchase_stock',
          'ges_purchase',
          'ges_stock',
                          
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [                   
        "views/ges_inh_stock_production_lot.xml",                                
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
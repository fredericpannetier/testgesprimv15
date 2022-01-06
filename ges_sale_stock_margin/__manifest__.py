# -*- coding: utf-8 -*-
{
    'name': "ges_sale_stock_margin",

    'summary': """
        ges_sale_stock_margin""",

    'description': """
        ges_sale_stock_margin
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
          'stock',
          'ges_sale',
          'ges_stock',
          'ges_sale_stock',
          'ges_purchase_stock',
          'sale_stock_margin',
                          
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [                   
                                 
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
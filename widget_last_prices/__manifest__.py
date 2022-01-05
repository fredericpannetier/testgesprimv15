# -*- coding: utf-8 -*-
{
    'name': "widget_last_prices",

    'summary': """
        widget_last_prices""",

    'description': """
        Add a widget button to show the last 5 prices for the product for the current customer
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'widget_last_prices',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [           
          'sale',                                
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [        
        "views/di_inh_sale_views.xml",                              
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'qweb': ['static/xml/widget_last_prices.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
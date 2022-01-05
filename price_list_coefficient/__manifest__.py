# -*- coding: utf-8 -*-
{
    'name': "Price list coefficient",

    'summary': """
        Price list coefficient""",

    'description': """
        This module allows you to add a coefficient in the price calculation formula
        This coefficient increases the base price used in the formula
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': ' ',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'base_setup',
        'sale',
        ],

    # always loaded
    'data': [
         "views/di_inh_product_pricelist_views.xml",                                                                 
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
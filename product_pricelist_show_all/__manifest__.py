# -*- coding: utf-8 -*-
{
    'name': "product_pricelist_show_all",

    'summary': """
        product_pricelist_show_all""",

    'description': """
      Show all the rules applicable to the product via the button Extra prices
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': '',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'product',
        'sale',                                                  
        ],

    # always loaded
    'data': [
        "data/action.xml",   
        "views/di_inh_product_pricelist_views.xml",
        "views/di_action_manager.xml",        
        "reports/di_product_pricelists_reports.xml",
        "security/ir.model.access.csv",                                                                         
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
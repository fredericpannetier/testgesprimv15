# -*- coding: utf-8 -*-
{
    'name': "tax_on_tax",

    'summary': """
        tax_on_tax""",

    'description': """
      Give the possibility to add a level of tax on a tax
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'tax_on_tax',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'account',
        'sale'                                                        
        ],

    # always loaded
    'data': [  
        "views/di_inh_account_view.xml",                                                                      
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
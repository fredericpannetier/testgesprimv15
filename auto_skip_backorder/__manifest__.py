# -*- coding: utf-8 -*-
{
    'name': "auto_skip_backorder",

    'summary': """
        auto_skip_backorder""",

    'description': """      
      If installed, Odoo does not ask if it should create a backorder, it just does not.
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
        'stock'                                                 
        ],

    # always loaded
    'data': [                                                                                    
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
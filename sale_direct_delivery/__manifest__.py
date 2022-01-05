# -*- coding: utf-8 -*-
{
    'name': "sale_direct_delivery",

    'summary': """
        sale_direct_delivery""",

    'description': """
      Confirm quotations, assign products and validate deliveries
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'sale_direct_delivery',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'account',
        'sale',
        'delivery',
        'popup'                                                      
        ],

    # always loaded
    'data': [  
        'security/ir.model.access.csv',
        "views/di_wiz_direct_delivery_view.xml",                                                                      
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
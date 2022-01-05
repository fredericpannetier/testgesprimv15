# -*- coding: utf-8 -*-
{
    'name': "purchase_auto_batch",

    'summary': """
        purchase_auto_batch""",

    'description': """      
      Give the possibility to auto complete the batch number in the receipts.
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
        'purchase',
        'delivery'                                                 
        ],

    # always loaded
    'data': [        
        "views/di_inh_res_config_settings_views.xml",                                                                     
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
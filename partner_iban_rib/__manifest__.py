# -*- coding: utf-8 -*-
{
    'name': "partner_iban_rib",

    'summary': """
        partner_iban_rib""",

    'description': """      
      Add fields to store iban/ rib informations with controls 
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
        'account'                                                   
        ],

    # always loaded
    'data': [            
        "views/di_inh_res_partner_bank_view.xml",                                                                                
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
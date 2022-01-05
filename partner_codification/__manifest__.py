# -*- coding: utf-8 -*-
{
    'name': "partner_codification",

    'summary': """
        partner_codification""",

    'description': """
      Make the ref required and easier to find.
      Give the possibility to auto complete the ref
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
        'base_setup',                                                    
        ],

    # always loaded
    'data': [
        "data/ir_sequence_data.xml",        
        "views/di_inh_res_partner_view.xml",
        "views/di_inh_res_config_settings_views.xml",                                                                     
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
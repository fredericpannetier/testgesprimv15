# -*- coding: utf-8 -*-
{
    'name': "LogBook",

    'summary': """
        Logbook recording""",

    'description': """
      This module allow to record/consult sensitives
      operations and other important informations from
      odoo daily usage
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
        ],

    # always loaded
    'data': [
        "views/di_logbook_views.xml",
        "security/ir.model.access.csv",                                                                     
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
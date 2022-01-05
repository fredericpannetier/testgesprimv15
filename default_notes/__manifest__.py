# -*- coding: utf-8 -*-
{
    'name': "default_note",

    'summary': """
        default_note""",

    'description': """
        Add a table that let the user to configure some texts that will automatically be printed on selected documents 
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'difmiadi',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'base_setup',
        'sale',
        'purchase', 
        'delivery',
        'stock',
        'account',                                                     
        ],

    # always loaded
    'data': [
        "views/di_default_note_views.xml",
        "reports/di_inh_reports.xml",        
        "security/ir.model.access.csv",                                                                     
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': True,    
}
# -*- coding: utf-8 -*-
{
    'name': "always_bottom_chatter",

    'summary': """
        always_bottom_chatter""",

    'description': """
        Place the chatter at the bottom of the page even if the page is wide enough.
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': '',
    'version': '14',

    # any module necessary for this one to work correctly
        # any module necessary for this one to work correctly
    'depends': [                                             
        'web',                                
        ],
    # always loaded
    'data': [                
        "views/di_templates.xml"      
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

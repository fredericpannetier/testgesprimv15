# -*- coding: utf-8 -*-
{
    'name': "Purchase Grid",

    'summary': """
        Purchase Grid""",

    'description': """
        This module allow to import previous purchases into new purchase order
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
        'purchase',                                                    
        ],

    # always loaded
    'data': [
        "views/di_purchase_grid_view.xml",
        "views/di_inherited_purchase_view.xml",
        "views/di_inh_res_config_settings_views.xml",
        "security/ir.model.access.csv",                                                                     
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': True,    
}
# -*- coding: utf-8 -*-
{
    'name': "ges_label_printing",

    'summary': """
        ges_label_printing""",

    'ges_label_printing': """
        ges_tables
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'gesprim',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [  
          'base',
          'product',
         'delivery',
          'stock',
         'ges_menu',
         'ges_tables',
         'ges_stock', 
         'printing',
                                        
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [
        "wizards/ges_print_etiq_wiz.xml",
        "menu/ges_menu.xml",         
        "views/ges_inh_res_config_settings_views.xml",
        "data/ges_default_settings.xml",      
        "security/ir.model.access.csv",                     
     ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
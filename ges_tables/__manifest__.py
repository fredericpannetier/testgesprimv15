# -*- coding: utf-8 -*-
{
    'name': "ges_tables",

    'summary': """
        ges_tables""",

    'description': """
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
         'ges_menu',  
#          'uom',                              
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [
        "data/ges_default_settings.xml",        
         "views/ges_inh_product_view.xml",            
         "views/ges_tables_view.xml",
         "views/ges_inh_uom_view.xml",
#          "views/ges_pallet_view.xml",    
         "views/ges_inh_res_partner_views.xml",   
         "views/ges_picker_view.xml",
         "views/ges_inh_multi_table_view.xml",  
         "security/ir.model.access.csv",
         "menu/ges_menu.xml",
     ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
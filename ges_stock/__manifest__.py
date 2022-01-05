# -*- coding: utf-8 -*-
{
    'name': "ges_stock",

    'summary': """
        ges_stock""",

    'description': """
        Surcharge des stocks
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
        'stock',
#         'export_stockinfo_xls',   
        'ges_tables',        
#         'ges_delivery',
#         'default_notes',  
                                 
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [   
        "views/ges_inh_stock_production_lot_views.xml", 
        "views/ges_inh_stock_move_views.xml",
        "views/ges_inventory_views.xml",
        "views/ges_inh_stock_picking.xml",
        "views/ges_inh_stock_quant_views.xml",
        'views/ges_wizard_export_stock_info_view.xml',
#         'views/ges_action_manager.xml',
        "wizards/ges_print_inventory_wiz.xml",
        "reports/ges_report_inventory.xml", 
        "reports/ges_inh_delivery_reports.xml",
        "reports/ges_inh_report_traceability.xml",                
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
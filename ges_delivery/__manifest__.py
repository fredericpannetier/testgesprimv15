# -*- coding: utf-8 -*-
{
    'name': "ges_delivery",

    'summary': """
        ges_delivery""",

    'description': """
        ges_delivery
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
        'sale',
        'ges_sale',
        'ges_stock',
        'ges_palletization',  
        'ges_sale_stock',                      
        ],

# 'difmiadi_agro',

    # always loaded
    'data': [  
        'wizards/ges_bord_trp_wiz.xml',
        'wizards/ges_carrier_ctrl_wiz.xml',        
        'reports/ges_report_bordtrp.xml',
        'reports/ges_report_carrier_ctrl.xml',
        'views/ges_inh_sale_views.xml',
        'views/ges_inh_stock_picking.xml',
        'views/ges_inh_res_partner_views.xml',
        'wizards/ges_inh_choose_delivery_carrier_views.xml',
        "security/ir.model.access.csv",      
        'views/ges_inh_delivery_view.xml',  
        'menu/ges_menu.xml',                                                                  
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
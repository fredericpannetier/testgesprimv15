# -*- coding: utf-8 -*-
{
    'name': "gesprim_menu",

    'summary': """
        gesprim_menu""",

    'description': """
        Need to be installed before any other Gesprim Module
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': ' ',
    'version': '14',

    # any module necessary for this one to work correctly
        # any module necessary for this one to work correctly
    'depends': [ 
        'base',
        'product',
        'sale',
        'sale_management',
        'stock',
        'sale_stock',
        'delivery',                     
        'purchase',
        'sale_margin',
        'account',     
        'logbook',
        'partner_address_improvement', 
        'partner_codification', 
        'product_codification', 
        'partner_iban_rib', 
        'partner_vat_auto', 
        'tax_on_tax', 
        'sale_direct_delivery',
        'sale_direct_invoice',
        'sale_grid',
        'purchase_grid',       
        'purchase_auto_batch',
        'purchase_direct_delivery',
        'auto_skip_backorder',
        'price_list_coefficient',
        'sale_order_toinvoice_period',
        'multi_table',
        'default_notes',
#         'accounting_transfer',
        # 'cost_auto_update',
        'partner_credit_limit',
        #'price_list_coefficient',
        'product_pricelist_show_all',
        'printing',  
        'widget_last_prices', 
        'always_bottom_chatter',
        'web_sheet_full_width',
#         'popup',
#         'billing_statement',
#         'cmp',
        ],
            
#             'ges_cde_achats',
#         'ges_cde_ventes',
#         'ges_factures',
#         'ges_stocks',
#         'ges_transport',
    # always loaded
    'data': [
        "views/ges_inh_res_config_settings_views.xml",
        "data/ges_groups.xml",
        "data/ges_default_settings.xml",
        "menu/ges_menu.xml",                                        
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
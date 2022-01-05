# -*- coding: utf-8 -*-
{
    'name': "ges_sale",

    'summary': """
        ges_sale""",

    'description': """
        ges_sale
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
          'sale',
          'ges_tables',
#           'ges_stock',
#           'ges_delivery',
                          
        ],
# 'difmiadi_agro',

    # always loaded
    'data': [        

        "data/ges_groups.xml",             
        "security/ir.model.access.csv",   
        "views/ges_inh_sale_views.xml",
        "views/ges_inh_partner_views.xml",
        "reports/ges_report_forecast.xml",
        "reports/ges_sale_stat.xml",
        "wizards/ges_print_forecast_wiz.xml",        
        "reports/ges_inh_sale_reports.xml",  
        "menu/ges_menu.xml",        

                              
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
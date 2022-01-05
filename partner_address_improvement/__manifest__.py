# -*- coding: utf-8 -*-
{
    'name': "Partner adress improvement",

    'summary': """
        Partner adress improvement""",

    'description': """
        This module allow to specify default delivery/invoice adress for partners with multiple adresses
        This module also provide city adress visibility on adress selection from sale order form
        Only parent partner can be used for order, not adresses and contacts
        Delivery and invoice adresses can only be choosed from sale order partner adresses
        Adress format in form view has been modified for french localization
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
        'sale',
        'purchase',                                                   
        ],

    # always loaded
    'data': [
        "views/di_inh_res_partner_views.xml",
        "views/di_inherited_sale_view.xml",
        "views/di_inh_purchase_views.xml",                                                                   
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
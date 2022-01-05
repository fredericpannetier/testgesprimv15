# -*- coding: utf-8 -*-
{
    'name': "partner_vat_auto",

    'summary': """
        partner_vat_auto""",

    'description': """
      Autocomplete vat number with siren number
    """,

    'author': "Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'partner_vat_auto',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'base_setup', 
        'l10n_fr',                                                   
        ],

    # always loaded
    'data': [                                                                        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,    
}
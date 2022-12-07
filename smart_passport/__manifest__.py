# -*- coding: utf-8 -*-
{
    'name': "Smart Passport",

    'summary': """
       This smart passport module provide the api to help you to sign in from mobile app.
         You can connect your smart ERP everywhere without web browser""",

    'description': """
       This smart passport module provide the api to help you to sign in from mobile app.
         You can connect your smart ERP everywhere without web browser. 
    """,

    'author': "Smartlife Tech Inc",
    'website': "http://www.smartlifevn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Smartlife',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
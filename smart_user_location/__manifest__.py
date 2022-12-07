# -*- coding: utf-8 -*-
{
    'name': "Smart Location",

    'summary': """
       Danh mục địa danh hành chính 3 cấp của Việt Nam
       """,

    'description': """
        Danh mục địa danh hành chính 3 cấp của Việt Nam
    """,

    'author': "SmartLife",
    'website': "smartlifevn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'SmartLife',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/tinh.xml',
        'data/huyen.xml',
        'data/xa1.xml',
        'data/xa2.xml',
        'data/xa3.xml',          
        'views/view_employee.xml',
        'views/view_company.xml',
        'views/view_respartner.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
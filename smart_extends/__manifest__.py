# -*- coding: utf-8 -*-
{
    'name': "Smart Extends",

    'summary': """
       This module supply extention plugins for customize function
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Thiep Wong & team",
    'website': "http://www.smartlifevn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup','web','base_import',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [
        'static/src/xml/invoice.xml',
        'static/src/xml/base_import_or.xml',
    ],
}
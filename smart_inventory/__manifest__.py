# -*- coding: utf-8 -*-
{
    'name': "Smart Inventory",

    'summary': """
        This module process the stock inventory for purchase and sale.
      developed by Thiep Wong & SML development team""",

    'description': """
        Supply stock inventory report and management
    """,

    'author': "SmartLife company",
    'website': "http://www.smartlifevn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Smartlife',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','smart_invoice'],
    'qweb': [
        'static/src/xml/button.xml',
    ],
    # always loaded
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'views/stock_views.xml',
        'reports/stock_picking_print_views.xml', 
        'reports/stock_card_report.xml',
        'reports/stock_inventory_report.xml', 
        'wizards/stock_inventory_report_wizard.xml',
        'wizards/stock_card_report_wizard.xml',
        'data/product_data.xml',
        'security/remove_menuitem.xml',
        'views/stock_inventory_manager.xml',
        'data/product_data.xml'
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
# -*- coding: utf-8 -*-
{
    'name': "Smart Sale",

    'summary': """
        This is smart purchase module, developing by Thiep Wong & team.
        Process the purchase order, and reporting.
      """,

    'description': """
        This is smart purchase module, developing by Thiep Wong & team.
        Process the purchase order, and reporting.
    """,

    'author': "Smartlife Company",
    'website': "http://www.smartlifevn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base','sale'],
    'depends': ['l10n_vn','sale','sale_stock','sale_management','stock'],
    'qweb': [
        'static/src/xml/button.xml',
    ],
    # always loaded
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'security/remove_menuitem.xml',
        'views/sale_order_views.xml',
        'views/sale_menu_views.xml',
        'views/stock_picking_view.xml',

        'reports/sale_report_templates.xml',
        # 'reports/reportsalejournal_view.xml',
        
        'reports/report_sale_journal.xml', 
        'reports/report_sale_journal_detail_by_goods.xml',
        'reports/report_sale_journal_detail_by_customers.xml',
        'reports/report_sale_journal_detail_by_employees.xml',
        'reports/report_sale_general_by_goods.xml',
        'reports/report_sale_general_by_customers.xml',
        'reports/report_sale_general_by_employees.xml',


        'wizard/report_sale_journal.xml',
        'wizard/report_sale_general.xml',
        'wizard/report_sale_detail.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],  
    'installable': True,
}
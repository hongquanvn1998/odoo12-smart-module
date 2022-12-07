# -*- coding: utf-8 -*-
{
    'name': "Smart Purchase",

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
    'category': 'Sale & Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_stock','purchase','stock_account','stock','account'],

    # always loaded
    'data': [
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/purchase_order_views.xml',
        'views/product_supplierinfo_view.xml',
        'views/stock_picking_view.xml',
        'reports/purchase_quotation_templates.xml',
        'reports/purchase_journal_report_template.xml',

        'wizards/purchase_journal_report.xml', 
        'wizards/purchase_journal_general_report.xml',
        'wizards/purchase_journal_detail_report.xml',

        'reports/report_purchase_journal.xml',

        'reports/report_purchase_general_goods.xml',
        'reports/report_purchase_general_vendors.xml',
        'reports/report_purchase_general_employees.xml',

        'reports/report_purchase_journal_detail_goods.xml',
        'reports/report_purchase_journal_detail_vendors.xml',
        'reports/report_purchase_journal_detail_employees.xml',

        'reports/purchase_journal_detail_report_template.xml',
        'reports/purchase_journal_general_report_template.xml',
        'views/res_partner_views.xml',

        'reports/purchase_quotation_templates.xml',
        'reports/purchase_order_templates.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
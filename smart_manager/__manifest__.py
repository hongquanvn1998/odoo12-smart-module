# -*- coding: utf-8 -*-
{
    'name': "Smart Manager",

    'summary': """
      Đây là phân hệ quản trị khách hàng và các module của Smart ERP
      """,

    'description': """
        Nhân viên Smartlife sẽ quản trị khách hàng và các module của hệ thống qua phân hệ này
    """,

    'author': "Smartlife Software R&D teams",
    'website': "http://smartlifevn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Smartlife',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'sale','smart_sale','smart_user_location','smart_invoice'],

    # always loaded
    'data': [
        # 'security/smart_manager_security.xml',
        'security/ir.model.access.csv',
        'views/register_view.xml',     
        'views/business_category_view.xml',  
        'views/app_module_view.xml',
        'views/product_view.xml', 
        'views/res_partner_view.xml',
        'views/register_form.xml', 
        'views/res_config_settings_view.xml',
        'views/sale_order_view.xml',

        'wizard/wizard_customer.xml',
        'wizard/wizard_partner.xml',
        'wizard/wizard_order.xml',

        'reports/report_customer.xml',
        'reports/report_partner.xml',
        'reports/report_order.xml',
        'reports/report_traffic_view.xml',

        'views/manage_menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
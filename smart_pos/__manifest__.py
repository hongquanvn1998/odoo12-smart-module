# -*- coding: utf-8 -*-
{
    'name': "Smart POS",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','account','web_groupby_expand','smart_user_location','smart_inventory','smart_invoice'],
    # always loaded
    'data': [
        # 'demo/demo.xml',
        'security/smart_pos_securiry.xml',
        'security/ir.model.access.csv',
        'views/shop_layout.xml',
        'views/views.xml',
        'views/pos_dashboard.xml',
        'views/pos_account_journal_view.xml',
        'views/pos_session_view.xml',
        'data/smart_pos_data.xml',
        'reports/report_end_of_day_by_goods.xml',
        'reports/report_end_of_day_by_receipts_expenses.xml',
        'reports/report_end_of_day_by_sale.xml',
        'reports/report_sale_by_partner.xml',
        'reports/report_reward_point.xml',
        'reports/report_reward_point_history.xml',

        # 'reports/report_sale_by_employee.xml',
        # 'reports/report_financial.xml',
        'reports/report_goods_by_profit.xml',
        'reports/report_goods_by_sale.xml',
        'reports/report_sale_by_employee.xml',
        'reports/report_sale_by_profit.xml',
        'reports/report_sale_by_time.xml',
        'reports/report_revenue.xml',
        'wizard/wizard_end_of_day.xml',
        'wizard/wizard_goods.xml',
        'wizard/wizard_financial.xml',
        'wizard/wizard_sale.xml',
        'wizard/wizard_revenue.xml',
        'wizard/wizard_employees.xml',
        'wizard/wizard_partner.xml',
        'wizard/wizard_reward_point.xml',
        'wizard/wizard_reward_point_history.xml',
        
        # 'views/pos_shifts.xml',
        'views/pos_orders.xml',
        'views/pos_config_general.xml',
        'views/pos_config_counters.xml',
        'views/pos_payment_method.xml',
        'views/pos_manage_customer.xml',
        'views/pos_manage_list_price.xml',
        'views/pos_manage_product.xml',
        #  'reports/report_sale_general_by_employees.xml',
        'views/res_partner_view.xml',
        'views/res_users_view.xml',
        'views/reward_point_views.xml',
        'views/pos_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application' :True
}
# -*- coding: utf-8 -*-
{
    'name': "Smart Accounting",

    'summary': """
         This is smartlife compayny's accounting system""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Thiep Wong",
    'website': "http://www.smartlifevn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.5',

    # any module necessary for this one to work correctly
    'depends': ['l10n_vn','account'],

    # always loaded
    'data': [
        'data/product_data.xml', 
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/account_pdf_reports.xml',
        'views/account_reports_settings.xml',
        'views/account_report.xml',
        'views/account_receipt_view.xml',
        'views/account_receipt_views.xml',
        'views/account_menu.xml',
        'wizards/partner_ledger.xml',
        'wizards/general_ledger.xml',
        'wizards/trial_balance.xml',
        'wizards/balance_sheet.xml',
        'wizards/profit_and_loss.xml',
        'wizards/tax_report.xml',
        'wizards/aged_partner.xml',
        'wizards/journal_audit.xml',
        'wizards/cash_ledger.xml',
        'wizards/all_balance_sheet.xml',
        'wizards/business_activities.xml',
        'wizards/cash_flows.xml',
        'wizards/account_balance_sheet.xml',
        'reports/report.xml',
        'reports/report_partner_ledger.xml',
        'reports/report_general_ledger.xml',
        'reports/report_trial_balance.xml',
        'reports/report_financial.xml',
        'reports/report_tax.xml',
        'reports/report_aged_partner.xml',
        'reports/report_journal_audit.xml',
        'reports/report_cash_ledger.xml',
        'reports/report_all_balance_sheet.xml',
        'reports/report_business_activities.xml',
        'reports/report_cash_flows.xml',
        'reports/report_balance_sheet.xml',
        'reports/payment_receipt_print_view.xml',
        'reports/payment_receipt_print_a5view.xml',
        'views/account.xml',
        'views/account_invoice_supplier_form.xml',
        'views/account_invoice_template.xml',
        'reports/sale_invoice_print_view.xml',
        'reports/sale_invoice_untax_print_view.xml',
        'reports/sale_accounting_document_print_view.xml',
        'views/report_templates.xml',
        'views/account_invoice_template_view.xml',
        'views/account_payment_view.xml',
        'views/account_invoice_views.xml',
        'security/remove_menuitem.xml',
    ],
    # only loaded in demonstration mode 
    
    'application': True,
    'images': ['static/description/banner.gif'],
}
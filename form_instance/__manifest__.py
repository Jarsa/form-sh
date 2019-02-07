# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Form Instance',
    'summary': 'Module that install Form Instance',
    'version': '12.0.1.0.0',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'account_accountant',
        'l10n_mx',
        'purchase',
        'crm',
        'timesheet_grid',
        'board',
        'repair',
        'mrp_plm_survey',
        'quality_control',
        'hr_attendance',
        'hr_appraisal',
        'hr_holidays',
        'sign',
        'helpdesk',
        'documents',
        'bo_import_direct_drive_sheet',
        'mailgun',
        'mail_tracking_mailgun',
        'account_xunnel',
        'mrp_production_request',
        'sale_stock_sample',
        'sale_to_plm_eco',
        'stock_uom_equivalence',
        'account_currency_rate_difference_reference',
        'account_skip_exchange_reversal',
        'account_tax_cash_basis_reference',
        'res_currency_rate_custom_decimals',
        'l10n_mx_edi_partner_defaults',
        'l10n_mx_edi_addendas',
        'l10n_mx_edi_bank',
        'l10n_mx_edi_reports',
        'sale_request',
        'mrp_product_alternative',
        'mrp_auto_assign',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mrp_workorder_view.xml',
        'views/stock_backorder_confirmation_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
    ],
}

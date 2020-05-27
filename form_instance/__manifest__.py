# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Form Instance',
    'summary': 'Module that install Form Instance',
    'version': '12.0.1.0.2',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'account_accountant',
        'l10n_mx',
        'purchase',
        'crm',
        'contacts',
        'timesheet_grid',
        'board',
        'repair',
        'mrp_plm_survey',
        'documents',
        'bo_import_direct_drive_sheet',
        'mailgun',
        'mail_tracking_mailgun',
        'account_xunnel',
        'mrp_production_request',
        'report_acount_invoice_form',
        'report_purchase_order_form',
        'report_stock_picking_form',
        'report_sale_order_form',
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
        'mrp_production_bom_alternative',
        'mrp_auto_assign',
        'product_code_mandatory',
        'product_code_unique',
        'base_user_role',
        'stock_no_negative',
        'web_m2x_options',
        'mrp_production_plan',
        'mrp_production_limit',
        'mrp_plm_control_version_bom',
        'sale_order_product_reference_partner',
        'stock_mts_mto_rule',
        'sale_order_invoice_merge_qty',
        'stock_picking_name_reference_change',
        'account_reports',
        'mrp_production_request_produce_location',
        'mrp_production_surplus',
        'product_category_validation',
        'quality',
        'quality_control',
        'account_aged_partner_balance_by_currency',
        'cost_margin_utility_report',
    ],
    'data': [
        'data/product_template.xml',
        'data/ir_config_parameter.xml',
        'data/ir_sequence_data.xml',
        'data/ir_base_automation_data.xml',
        'data/ir_cron.xml',
        'security/security.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/mrp_workorder_view.xml',
        'views/stock_backorder_confirmation_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/stock_picking_view.xml',
        'views/mrp_production_request_view.xml',
        'views/mrp_production_plan_view.xml',
        'views/mrp_production_view.xml',
        'views/res_partner_view.xml',
        'views/account_payment_view.xml',
        'views/mrp_bom_view.xml',
        'views/stock_picking_type_view.xml',
        'views/stock_quant_view.xml',
        'views/stock_inventory_view.xml',
        'views/root_cause_quality_view.xml',
        'views/mrp_routing_view.xml',
        'views/product_template_view.xml',
        'views/stock_move_line_view.xml',
        'views/crm_lead_view.xml',
        'views/stock_warehouse_view.xml',
        'views/mrp_document_view.xml',
        'wizards/change_production_qty_views.xml',
        'views/quality_alert_views.xml',
        'views/quality_point_view.xml',
        'views/mrp_production_update_reason_view.xml',
    ],
}

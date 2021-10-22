# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Form Instance',
    'summary': 'Module that install Form Instance',
    'version': '14.0.1.0.5',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'account_accountant',
        'l10n_mx',
        'crm',
        'contacts',
        'project',
        'sale_management',
        'mrp_plm',
        'stock_account',
        'documents',
        'mrp',
        'mrp_request',
        'report_purchase_order_form',
        'l10n_mx_edi',
        'l10n_mx_edi_account_followup',
        'l10n_mx_edi_uuid',
        'sale_request',
        'mrp_production_plan',
        'mrp_plm_control_version_bom',
        'sale_order_product_reference_partner',
        'quality_control',
        'quality_mrp_workorder',
        'quality_mrp',
        'account_aged_by_currency_report',
        'purchase_order_secondary_unit',
        'stock_secondary_unit',
    ],
    'data': [
        'data/product_template.xml',
        'data/ir_config_parameter.xml',
        'data/ir_sequence_data.xml',
        'data/ir_base_automation_data.xml',
        'data/ir_cron.xml',
        'data/account_tag.xml',
        'security/security.xml',
        'security/rules.xml',
        'views/mrp_workorder_view.xml',
        'views/stock_backorder_confirmation_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/stock_picking_view.xml',
        'views/mrp_request_view.xml',
        'views/mrp_production_plan_view.xml',
        'views/mrp_production_view.xml',
        'views/res_partner_view.xml',
        'views/mrp_workcenter_view.xml',
        'views/account_payment_view.xml',
        'views/mrp_bom_view.xml',
        'views/stock_picking_type_view.xml',
        'views/stock_quant_view.xml',
        'views/stock_inventory_view.xml',
        'views/product_template_view.xml',
        'views/stock_move_line_view.xml',
        'views/crm_lead_view.xml',
        'views/stock_warehouse_orderpoint_view.xml',
        'views/mrp_document_view.xml',
        'wizards/change_production_qty_views.xml',
        'views/quality_alert_views.xml',
        'views/mrp_production_update_reason_view.xml',
        'views/sale_request_view.xml',
        'security/ir.model.access.csv',
    ],
}

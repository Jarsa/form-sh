{
    'name': 'Sale Request',
    'summary': 'Create Sale Order From Sale Requests by Product',
    'version': '17.0.1.0.0',
    'author': 'Jarsa Sistemas S.A. de C.V., Odoo Community Association (OCA)',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'LGPL-3',
    'depends': [
        'sale',  # 'sale_management' is now 'sale' in Odoo 17
        'sale_stock',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/ir_config_parameter.xml',
        'security/sale_request_security.xml',
        'security/ir.model.access.csv',
        'wizards/create_sale_order_wizard_view.xml',
        'wizards/link_sale_order_wizard_view.xml',
        'views/sale_order_view.xml',
        'views/sale_request_view.xml',
        'views/sale_order_report_view.xml',
    ],
    'installable': True,
    'application': True,  # Mandatory for Odoo 17
    'auto_install': False,  # Prevents auto-installation unless required
}

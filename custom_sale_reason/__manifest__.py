{
    "name": "Sale Confirmation and Cancellation Reason",
    "version": "17.0.1.0.0",
    "depends": ["sale_management"],
    "category": "Sales",
    'license': 'LGPL-3',
    "author": "[HBM] - GW",
    "description": "Adds a reason popup when confirming or cancelling quotations.",
    "data": [
        'security/ir.model.access.csv',
        'data/sale_reason_option_data.xml',
        "views/sale_reason_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}

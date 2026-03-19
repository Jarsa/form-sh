{
    'name': 'Invoice View Fix',
    'version': '17.0.1.0.0',
    'summary': 'Fix SelectionField crash when a stored value is not found in selection options',
    'author': '[HBM] - GW',
    'category': 'Technical',
    'depends': ['web', 'account'],
    'assets': {
        'web.assets_backend': [
            'invoice_view_fix/static/src/js/selection_field_fix.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}

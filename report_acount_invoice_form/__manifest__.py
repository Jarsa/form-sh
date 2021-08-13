# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'Report invoice for FORM',
    'external_dependencies': {
        'python': [
            'num2words',
        ],
    },
    'summary': 'Custom invoice report ',
    'version': '12.0.1.0.0',
    'category': 'Report',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'account',
        'l10n_mx_edi',
    ],
    'data': [
        'views/invoice_template.xml',
    ],
}

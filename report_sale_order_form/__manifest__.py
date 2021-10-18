# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'Report sale order for FORM',
    'external_dependencies': {
        'python': [
            'num2words',
        ],
    },
    'summary': 'Custom sale order report ',
    'version': '14.0.1.0.0',
    'category': 'Report',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'sale_request',
    ],
    'data': [
        'views/sale_order_template.xml',
    ],
}

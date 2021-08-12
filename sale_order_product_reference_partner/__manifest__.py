# Copyright 2019, Jarsa Sistemas S.A de C.V
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Form Sale Order Product Reference Partner',
    'summary': """
    This module add a field in product views to can link it
    to supplier in specific""",
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://www.jarsa.com.mx',
    'author': 'Jarsa Sistemas',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'sale_management',
        'stock',
        'sale_request',
    ],
    'data': [
        'views/product_product.xml',
        'data/ir_config_parameter.xml',
    ],
}

# Copyright 2019, Jarsa Sistemas S.A de C.V
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Form Stock Picking Name Reference Change',
    'summary': """
    This module change name origin form picking by a
    mrp order
    """,
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'website': 'https://www.jarsa.com.mx',
    'author': 'Jarsa Sistemas',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'sale_management',
        'stock',
        'mrp',
    ],
    'data': [
        'views/stock_picking_view.xml',
    ],
}

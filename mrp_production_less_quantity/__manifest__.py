# Copyright 2020, Jarsa Sistemas S.A de C.V
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Form MRP Production Less Quantity',
    'summary': """
    This module allows to decrease the original quantity of a Manufacturing
    Order if there are Workorders processed with less quantity than the
    original quantity.""",
    'version': '12.0.1.0.1',
    'category': 'Manufacture',
    'website': 'https://www.jarsa.com.mx',
    'author': 'Jarsa Sistemas',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'mrp',
    ],
}

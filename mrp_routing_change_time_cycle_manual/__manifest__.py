# Copyright 2019, Jarsa Sistemas S.A de C.V
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Form MRP Change format time manual Cycle',
    'summary': """
    This module change format from time to decimal number
    """,
    'version': '12.0.1.0.0',
    'category': 'Manufacture',
    'website': 'https://www.jarsa.com.mx',
    'author': 'Jarsa Sistemas',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'mrp',
    ],
    'data': [
        'views/mrp_routing_workcenter_view.xml',
    ],
}

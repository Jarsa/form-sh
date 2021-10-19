# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale to ECO',
    'summary': 'Module to create ECO from sale order',
    'version': '14.0.1.0.0',
    'category': 'Sale',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'sale_request',
    ],
    'data': [
        'wizard/eco_wizard_view.xml',
        'views/sale_order_view.xml',
        'views/mrp_eco_view.xml',
        'security/ir.model.access.csv',
    ],
}

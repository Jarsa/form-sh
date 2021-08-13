# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Produce Location to Manufacture Request',
    'summary': 'Define production locations based on product category',
    'version': '12.0.1.0.1',
    'category': 'Manufacture',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'mrp_production_request',
    ],
    'data': [
        'views/product_category_view.xml',
    ],
}

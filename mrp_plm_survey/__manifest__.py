# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'MRP PLM Survey',
    'summary': 'MRP PLM Survey',
    'version': '14.0.1.0.0',
    'category': 'mrp',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'survey',
        'mrp_plm',
    ],
    'data': [
        'views/eco_view.xml',
    ],
}

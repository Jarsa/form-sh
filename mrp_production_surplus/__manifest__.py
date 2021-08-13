# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'MRP Production Surplus',
    'version': '12.0.1.0.0',
    'category': 'Customs',
    'author': 'Jarsa Sistemas, Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'mrp',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/stock_picking_type_data.xml',
        'views/mrp_production_view.xml',
        'views/mrp_bom_view.xml',
    ],
}

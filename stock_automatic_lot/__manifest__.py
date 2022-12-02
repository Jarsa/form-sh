# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'Stock Production Lot Automatic',
    'summary': 'Give an automatic name to the lots from a sequence',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': False,
    'depends': [
        'stock',
        'mrp',
        'sale',
        'purchase',
    ],
    'data': [
        'data/stock_production_lot_data.xml',
        'wizards/mrp_product_produce_view.xml'
    ],
}

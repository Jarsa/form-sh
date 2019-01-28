# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'Sale Stock Sample',
    'summary': 'Create Sample Products for Customers',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'sale_request',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/stock_location_data.xml',
        'data/stock_picking_type_data.xml',
        'data/stock_location_route_data.xml',
        'views/stock_location_route_view.xml',
        'wizards/sale_stock_sample_procurement_wizard_view.xml',
        'views/sale_order_view.xml',
    ],
}

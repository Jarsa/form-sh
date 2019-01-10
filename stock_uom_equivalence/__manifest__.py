# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'Stock UoM Equivalence',
    'summary': 'Manage inventory in one UoM and reporting in a secondary UoM',
    'version': '12.0.1.0.0',
    'category': 'Stock',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': ['stock_account', ],
    'data': [
        'report/report_delivery_slip.xml',
        'report/report_picking.xml',
        'views/product_view.xml',
        'views/stock_move_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_quant_view.xml',
    ],
}

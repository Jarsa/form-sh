# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'MRP Production Plan',
    'summary': 'Schedule the production of the day',
    'version': '14.0.1.0.1',
    'category': 'Manufacture',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'mrp_request',
        'mrp_workorder',
        'stock_split_picking',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mrp_production_plan.xml',
        'views/product_category_view.xml',
        'data/ir_sequence.xml',
        'data/stock_picking_type.xml',
        'views/mrp_request_view.xml',
        'views/mrp_production_view.xml',
    ],
}

# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'MRP Production Plan',
    'summary': 'Schedule the production of the day',
    'version': '12.0.1.0.0',
    'category': 'Manufacture',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'mrp_production_request',
        'mrp_workorder',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mrp_production_plan.xml',
        'views/product_category_view.xml',
        'data/ir_sequence.xml',
    ],
}

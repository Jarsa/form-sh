# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    'name': 'MRP Production BoM Alternative',
    'summary': 'Select Alternative BoM in Manufacture Orders',
    'version': '12.0.1.0.0',
    'category': 'Manufacture',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': ['mrp', 'stock_available_unreserved'],
    'data': [
        'wizards/mrp_production_bom_alternative_wizard_view.xml',
        'views/mrp_production_view.xml',
    ],
}

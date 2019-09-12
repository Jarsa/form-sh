# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'product_category_validation',
    'summary': """Module that validates fields in relation to the chosen
    category""",
    'version': '12.0.1.0.1',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'product'
    ],
    'data': [
        'views/product_category_view.xml',
        'security/ir.model.access.csv',
    ],
}

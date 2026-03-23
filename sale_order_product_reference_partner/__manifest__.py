# Copyright 2019, Jarsa Sistemas S.A de C.V
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Referencia de Producto por Cliente',
    'summary': 'Vincula productos a clientes específicos y valida su uso en pedidos y requisiciones de venta',
    'version': '17.0.1.0.0',
    'category': 'Ventas',
    'website': 'https://www.jarsa.com.mx',
    'author': 'Jarsa Sistemas',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'sale_management',
        'stock',
        'sale_request',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'views/product_product.xml',
    ],
}

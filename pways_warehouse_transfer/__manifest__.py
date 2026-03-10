{
    'name': "Inter Warehouse Transfer",
    'version': '1.0',
    'author': 'Preciseways',
    'summary': """Internal transfer of goods from one warehouse to another warehouse""",
    'description':""" 
                    Internal transfer of goods from one warehouse to another warehouse
                    internal warehouse
                    Internal location
                    Inter transfer
                    Inter location
                    Inter warehouse
                """,
    "category": "warehouse",
    'depends': ['stock'],
    'data': [
        'data/stock_data.xml',
        'security/ir.model.access.csv',
        'views/stock_transfer_view.xml',
    ],
   'application': False,
    'installable': True,
    'price': 31,
    'currency': 'EUR',
    "images":['static/description/banner.jpg'],
    'live_test_url': 'https://preciseways.com',
    'license': 'OPL-1',
}

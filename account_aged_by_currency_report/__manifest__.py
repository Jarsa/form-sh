# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Reportes de Antigüedad de Saldos por Moneda',
    'summary': 'Permite filtrar los reportes de antigüedad de saldos por moneda extranjera',
    'version': '17.0.1.0.0',
    'category': 'Contabilidad',
    'website': 'https://www.jarsa.com.mx/',
    'author': 'Jarsa',
    'license': 'LGPL-3',
    'depends': [
        'account_reports',
    ],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'account_aged_by_currency_report/static/src/components/aged_by_currency_report/filters/filters.js',
            'account_aged_by_currency_report/static/src/components/aged_by_currency_report/filters/filters.xml',
        ],
    },
    'installable': True,
}

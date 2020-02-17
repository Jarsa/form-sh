# Copyright 2020, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Account Aged Partner Balance by Currency',
    'summary': 'Add Filter Currency to Aged Partner Balance',
    'version': '12.0.1.0.0',
    'category': 'Account',
    'website': 'https://www.jarsa.com.mx',
    'author': 'Jarsa Sistemas, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'account_reports',
    ],
    'data': [
        'views/search_template_views.xml',
    ],
}

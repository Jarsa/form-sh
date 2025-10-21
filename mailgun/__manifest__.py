# Copyright 2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Mailgun',
    'summary':
        'Setup the outgoing and incoming mail flow easily by using Mailgun',
    'category': 'Discuss',
    'version': '14.0.0.0.0',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'license': 'LGPL-3',
    'depends': [
        'mail',
    ],
    'data': [
        'data/ir_cron_data.xml',
    ],
    'installable': True,
}

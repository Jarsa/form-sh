# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data
        SET name='group_google_spreadsheet_import_manager', noupdate = 'f'
        WHERE name = 'group_google_import'
    """)

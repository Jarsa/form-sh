# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo import http
from odoo.http import request
from odoo.tools import misc
from odoo.addons.base_import.controllers.main import ImportController


class GoogleSpreadheet(ImportController):

    @http.route('/base_import/set_file', methods=['POST', 'GET'])
    def set_file(self, file, import_id, jsonp='callback', from_drive=""):
        import_id = int(import_id)
        if from_drive:
            base_import = request.env['base_import.import'].browse(import_id)
            sheet = request.env['google.spreadsheet'].search(
                [('model_id.model', '=', base_import.res_model)], limit=1)
            written = False
            if sheet:
                content = sheet._get_content(sheet.file_id.id_file)
                if content.status_code == 200:
                    written = base_import.write({
                        'file': content.content,
                        'file_name': 'google_export.csv',
                        'file_type': content.headers.get(
                            "Content-Type", False),
                    })
            return 'window.top.%s(%s)' % (
                misc.html_escape(jsonp), json.dumps({'result': written}))
        return super().set_file(file, import_id, jsonp)

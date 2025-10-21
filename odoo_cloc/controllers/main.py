# Copyright 2023 Jarsa
# License LGPL-3 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.tools.cloc import Cloc


class WebhookCloc(http.Controller):
    @http.route("/odoo_cloc/webhook/", type="json", auth="public", csrf=False)
    def _process_cloc(self):
        cloc = Cloc()
        cloc.count_database(self)
        code = cloc.code
        code.pop("odoo_cloc")
        return code

from odoo import models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.ondelete(at_uninstall=False)
    def _prevent_automatic_line_deletion(self):
        # Override: permite eliminar líneas de impuestos sin bloquear
        pass

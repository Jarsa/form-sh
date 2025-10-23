# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        "l10n_mx_edi.payment.method",
        string="Payment Way",
        help="This payment method will be used by default in the related "
        "documents (invoices, payments, and bank statements).",
        default=lambda self: self.env.ref("l10n_mx_edi.payment_method_otros", raise_if_not_found=False),
    )
    def _get_usage_default(self):
        selection = self._get_usage_selection()
        # Busca P01 en la selección, si existe
        for code, label in selection:
            if code == "P01":
                return code
        # Si no existe, regresa el primer valor permitido
        return selection[0][0] if selection else False
    
    def _get_usage_selection(self):
        return self.env["account.move"].fields_get().get("l10n_mx_edi_usage").get("selection")

    l10n_mx_edi_usage = fields.Selection(
        _get_usage_selection,
        "Usage",
        default=lambda self: self._get_usage_default(),
        help="This usage will be used instead of the default one for invoices.",
    )

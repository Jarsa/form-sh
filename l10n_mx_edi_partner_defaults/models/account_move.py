
from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_usage_selection(self):
        return self.env["account.move"].fields_get().get("l10n_mx_edi_usage").get("selection")

    l10n_mx_edi_usage = fields.Selection(
        selection=_get_usage_selection,
        string="Fiscal Usage",
        store=True,
        default="S01",  # Valor permitido por la selección
        help="This usage will be used instead of the default one for invoices.",
    )

    l10n_mx_edi_payment_method_id = fields.Many2one(
        "l10n_mx_edi.payment.method", string="Payment Method", related="partner_id.commercial_partner_id.l10n_mx_edi_payment_method_id", store=True
    )

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        commercial_partner = self.partner_id.commercial_partner_id
        if commercial_partner:
            self.l10n_mx_edi_payment_method_id = commercial_partner.l10n_mx_edi_payment_method_id
            usage_values = [code for code, label in self._get_usage_selection()]
            if commercial_partner.l10n_mx_edi_usage in usage_values:
                self.l10n_mx_edi_usage = commercial_partner.l10n_mx_edi_usage
            else:
                self.l10n_mx_edi_usage = "S01"
        return res

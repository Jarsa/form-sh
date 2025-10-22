# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _post_invoice_edi(self, invoices, test_mode=False):
        edi_results = super()._post_invoice_edi(invoices, test_mode)
        if self.code != "cfdi_3_3":
            return edi_results

        # We will mark the field `l10n_mx_edi_signed_to_send` of the invoices that were signed successfully, to send
        # to the Customer an email about it.
        for invoice, edi_result in edi_results.items():
            if edi_result.get("error") or invoice.l10n_mx_edi_signed_to_send == "sent":
                continue
            invoice.l10n_mx_edi_signed_to_send = "to_send"
        return edi_results

from odoo import fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.split.payment.register"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        comodel_name="l10n_mx_edi.payment.method",
        string="Payment Way",
        readonly=False,
        help="Indicates the way the payment was/will be received, where the options could be: "
        "Cash, Nominal Check, Credit Card, etc.",
    )

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------

    # REVIEWED
    def _create_payment_vals_from_split_batch(self, batch_result):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_split_batch(batch_result)
        payment_vals["l10n_mx_edi_payment_method_id"] = self.l10n_mx_edi_payment_method_id.id
        return payment_vals

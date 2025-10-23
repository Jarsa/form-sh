from odoo import models


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        has_100_discout = self._check_discounts(invoice.invoice_line_ids)
        no_mxn = False
        if invoice.currency_id != invoice.company_currency_id:
            no_mxn = True
            if has_100_discout:
                # There is a line in route enterprise/l10n_mx_edi/models/account_edi_format.py
                # line 246 where make a validation than divide this fields amount_total_signed and amount_total
                # This only happennig when currency is not mxn, because of amount of translate invoice is
                # 0 make a mistake because the division bettwern 0 is not allowed.
                # For that reason I changed its value by one and store its original value in a few var
                # then after make super the method I returned its original value.
                old_amount_total_signed = invoice.amount_total_signed
                old_invoice_amount_total = invoice.amount_total
                invoice.write({
                    'amount_total_signed': 1,
                    'amount_total': 1,
                })

        values = super()._l10n_mx_edi_get_invoice_cfdi_values(invoice)
        if invoice.company_id.partner_id.commercial_partner_id != invoice.partner_id.commercial_partner_id:  # noqa
            return values
        invoice_lines = values["invoice_line_values"]
        values.update(
            {
                "document_type": "T",
                "payment_policy": None,
                "discount_amount": None,
                "total_amount_untaxed_wo_discount": sum(vals["total_wo_discount"] for vals in invoice_lines),
                "total_amount_untaxed_discount": sum(vals["discount_amount"] for vals in invoice_lines),
                "total_discount": lambda l, d: False,
                # NumRegIdTrib equal to None if Emisor == Receptor (CFDI type == T)
                "receiver_reg_trib": None,
            }
        )
        if has_100_discout:
            # changes values to 0 if has discount
            for invoice_line in values["invoice_line_values"]:
                invoice_line["discount_amount"] = 0
                new_price = (
                    invoice_line["line"].quantity * invoice_line["line"].price_unit)
                # This line is necesary to in xml file store the tag Importe
                invoice_line["total_wo_discount"] = new_price
            values["total_amount_untaxed_wo_discount"] = 0
            values["total_amount_untaxed_discount"] = 0

            if no_mxn:
                # Return the original value of fields amount_total_signed and amount_total
                invoice.write({
                    "amount_total_signed": old_amount_total_signed,
                    "amount_total": old_invoice_amount_total,
                })
                # Compute the correct rate currency
                rate = invoice.currency_id._get_rates(
                    self.env.company, invoice.invoice_date)
                values["currency_conversion_rate"] = 1 / rate[2]
        return values

    # This function check if all lines has discount of 100 percent
    def _check_discounts(self, invoice_line):
        has_100_percent = True
        for rec in invoice_line:
            if rec.discount != 100:
                has_100_percent = False
        return has_100_percent

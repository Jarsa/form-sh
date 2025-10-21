from odoo import models


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
        result = super()._l10n_mx_edi_get_invoice_cfdi_values(invoice)
        if not invoice.invoice_line_ids.mapped("tax_ids.invoice_repartition_line_ids").filtered(
            lambda r: r.tag_ids and r.tag_ids[0].name.lower() == "local"
        ):
            return result
        # Taxes
        tax_details_transferred = result["tax_details_transferred"]
        tax_details = []
        tax_details_local = []
        for tax in tax_details_transferred:
            if "Local" in tax["tax"].mapped("invoice_repartition_line_ids.tag_ids.name"):
                tax_details_local.append(tax)
                continue
            tax_details.append(tax)
        result["tax_details_transferred"] = tax_details
        # Withholding
        tax_details_withholding = result["tax_details_withholding"]
        tax_details = []
        withholding_details_local = []
        for tax in tax_details_withholding:
            if "Local" in tax["tax"].mapped("invoice_repartition_line_ids.tag_ids.name"):
                withholding_details_local.append(tax)
                continue
            tax_details.append(tax)
        result["tax_details_withholding"] = tax_details
        # Section for lines
        for line_vals in result["invoice_line_values"]:
            tax_details = []
            withholding_details = []
            for tax in line_vals["tax_details_transferred"]:
                if "Local" in tax["tax"].mapped("invoice_repartition_line_ids.tag_ids.name"):
                    continue
                tax_details.append(tax)
            for tax in line_vals["tax_details_withholding"]:
                if "Local" in tax["tax"].mapped("invoice_repartition_line_ids.tag_ids.name"):
                    continue
                withholding_details.append(tax)

            line_vals["tax_details_transferred"] = tax_details
            line_vals["tax_details_withholding"] = withholding_details
        result["total_tax_details_transferred"] = sum(vals["total"] for vals in result["tax_details_transferred"])
        result["total_tax_details_withholding"] = sum(vals["total"] for vals in result["tax_details_withholding"])
        # Totals for implocal
        result["tax_details_transferred_local"] = {
            "total": sum(tax["total"] for tax in tax_details_local),
            "tax_details_local": tax_details_local,
        }
        result["tax_details_withholding_local"] = {
            "total": sum(tax["total"] for tax in withholding_details_local),
            "withholding_details_local": withholding_details_local,
        }
        return result

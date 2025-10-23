from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import Controller, request

from odoo.addons.account.controllers.portal import PortalAccount as PA
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.web.controllers.main import Binary


class SendInvoiceAndXML(Controller):
    @http.route(
        [
            "/send_invoice_mail/<int:invoice_id>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def send_invoice_and_xml(self, invoice_id=None, **data):
        invoice = request.env["account.move"].browse(invoice_id)
        invoice.sudo()._generate_invoice_report(send=True)
        values = {
            "company": invoice.company_id,
            "user": request.env.user,
            "invoice": invoice,
        }
        return request.render("l10n_mx_portal.email_sent", values)

    @http.route(
        [
            "/generate_invoice/<int:order_id>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def generate_invoice(self, order_id=None, **data):
        sale_obj = request.env["sale.order"]
        sale = sale_obj.sudo().browse(order_id)
        if not sale.partner_id.vat:
            _message_post_helper(
                message=_("Please define your VAT, after try to generate the invoice again."),
                res_id=order_id,
                res_model="sale.order",
            )
            return request.redirect(sale.get_portal_url())
        if sale.invoice_status != "invoiced":
            invoice = sale._create_invoices()
            invoice.sudo().action_post()
            return request.redirect(sale.get_portal_url())
        reinvoice = sale.invoice_ids.l10n_mx_edi_action_reinvoice()
        if reinvoice:
            _message_post_helper(message=reinvoice, res_id=order_id, res_model="sale.order")
            return request.redirect(sale.get_portal_url())
        return request.redirect(sale.get_portal_url())


class PortalAccount(PA):
    @http.route(["/my/invoices/<int:invoice_id>"], type="http", auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        error = False
        try:
            invoice_sudo = self._document_check_access("account.move", invoice_id, access_token)
        except (AccessError, MissingError):
            error = True
        if error or report_type not in ("edi", "zip") or not download:
            return super().portal_my_invoice_detail(
                invoice_id=invoice_id, access_token=access_token, report_type=report_type, download=download, **kw
            )

        attachment_type = ".zip" if report_type == "zip" else ".xml"
        attachment = invoice_sudo.get_cfdi_att(attachment_type=attachment_type)
        request.env.su = True
        return Binary.content_common(self, id=attachment, download=True)

    @http.route(["/my/payment_complements"], type="http", auth="user", website=True)
    def my_payment_complements(self, **kw):
        domain = self._prepare_payments_domain(request.env.user.commercial_partner_id.id)
        values = {
            "payment_partner": request.env["account.payment"].search(domain),
            "page_name": "payment_complements",
        }
        return request.render("l10n_mx_portal.payment_complements", values)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "payment_count" not in counters:
            return values
        values["payment_count"] = (
            request.env["account.payment"].search_count([])
            if request.env["account.payment"].check_access_rights("read", raise_exception=False)
            else 0
        )
        return values

    def _prepare_payments_domain(self, partner_id):
        return [("partner_id", "child_of", partner_id), ("is_reconciled", "=", True)]

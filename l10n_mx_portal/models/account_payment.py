import base64
import io
import zipfile

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_count = fields.Integer(compute="_compute_payment_count")

    def l10n_mx_edi_my_payment_complements_zip(self):
        self = self.sudo()
        attachments_ids = self.edi_document_ids.attachment_id
        attachments_ids |= (
            self.env["ir.attachment"].search(
                [
                    ("res_id", "=", self.id),
                    ("res_model", "=", "account.payment"),
                    ("mimetype", "=", "application/pdf"),
                ],
                limit=1,
            )
            or self.l10n_mx_edi_create_payment_pdf()
        )
        attachment_file_id = self.l10n_mx_edi_retrieve_payment_complements_zip()
        #  The access token is added to the zip so that attachments created in
        #  previous versions without token can be downloaded from the portal.
        if attachment_file_id:
            attachment_file_id.generate_access_token()
            return attachment_file_id
        if attachments_ids:
            attachment_file_id = (
                self.l10n_mx_edi_create_zip(attachments_ids) if len(attachments_ids) > 1 else attachments_ids[0]
            )

        return attachment_file_id

    def l10n_mx_edi_retrieve_payment_complements_zip(self):
        domain = [
            ("res_id", "=", self.id),
            ("mimetype", "=", "application/zip"),
            ("res_model", "=", "account.payment"),
        ]
        return self.env["ir.attachment"].sudo().search(domain, limit=1)

    def l10n_mx_edi_create_zip(self, attachments_ids):
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, "w") as myzip:
            for attachment in attachments_ids:
                myzip.writestr(attachment.name, base64.b64decode(attachment.datas))
            myzip.close()
            zip_name = attachments_ids[0].name.replace(".xml", ".zip")
            values = {
                "name": zip_name,
                "type": "binary",
                "mimetype": "application/zip",
                "public": False,
                "datas": base64.b64encode(zip_stream.getvalue()),
                "res_id": attachments_ids[0].res_id,
                "res_model": "account.payment",
                "access_token": self.env["ir.attachment"]._generate_access_token(),
            }
        return self.env["ir.attachment"].create(values)

    def _compute_payment_count(self):
        self.payment_count = self.env["account.payment"].search_count([])

    def l10n_mx_edi_create_payment_pdf(self):
        self.ensure_one()
        report = self.env["ir.actions.report"]._get_report_from_name("account.report_payment_receipt")
        pdf_file = report._render(self.ids)
        if not pdf_file:
            return self.env["ir.attachment"]
        values = {
            "name": "%s.pdf" % (self.name or "").replace("/", "-"),
            "type": "binary",
            "public": False,
            "datas": base64.b64encode(pdf_file[0]),
            "mimetype": "application/pdf",
            "res_id": self.id,
            "res_model": "account.payment",
            "access_token": self.env["ir.attachment"]._generate_access_token(),
        }
        return self.env["ir.attachment"].create(values)

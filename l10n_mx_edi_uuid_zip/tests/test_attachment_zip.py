# Copyright 2019 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged

from odoo.addons.l10n_mx_edi_40.tests.common import TestMxEdiCommon


@tagged("post_install", "-at_install")
class TestAttachmentZip(TestMxEdiCommon):
    def test_attachment_zip(self):
        self.certificate._check_credentials()
        self.env.company.sudo().search([("name", "=", "ESCUELA KEMPER URGATE")]).write(
            {"name": "ESCUELA KEMPER URGATE TEST"}
        )
        self.env.user.company_id.write(
            {
                "name": "ESCUELA KEMPER URGATE",
            }
        )
        invoice = self.invoice
        invoice.action_post()
        self._process_documents_web_services(invoice, {"cfdi_3_3"})
        attach_zip = self.env["ir.attachment.zip"].create(
            {
                "attachment_ids": [(6, 0, invoice.edi_document_ids.mapped("attachment_id").ids)],
                "zip_name": "test01.zip",
            }
        )
        attach_zip._set_zip_file()
        # action = attach_zip._get_action_download()
        # TODO: add asserts reading zip content

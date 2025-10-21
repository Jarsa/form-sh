# Copyright 2018, Vauxoo, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import logging
from io import BytesIO

from lxml import etree, objectify

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.xml_utils import _check_with_xsd

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def l10n_mx_edi_is_expense(self):
        self.ensure_one()

        # Using sudo because we need to be as efficient as possible here
        # jumping the ACL process.
        if not self.sudo().res_model == "hr.expense" and not self.sudo().company_id.country_id == self.env.ref(
            "base.mx"
        ):
            return False
        return True

    # TODO: @luis_t This Method needs refactoring in order to comply with the linters.
    @api.model
    def l10n_mx_edi_is_cfdi33(self):  # pylint:disable=too-many-return-statements
        self.ensure_one()
        if not self.datas:
            return None
        try:
            datas = base64.b64decode(self.datas).replace(b"xmlns:schemaLocation", b"xsi:schemaLocation")
            cfdi = objectify.fromstring(datas)
        except (SyntaxError, ValueError):
            return None

        version = cfdi.get("Version")
        if version not in ["3.3", "4.0"]:
            return None
        attachment = self.sudo().env.ref("l10n_mx_edi.xsd_cached_cfdv33_xsd", False) if version == "3.3" else False
        schema = base64.b64decode(attachment.datas) if attachment else b""
        try:
            if hasattr(cfdi, "Addenda"):
                cfdi.remove(cfdi.Addenda)
            if not hasattr(cfdi, "Complemento"):
                return None
            if not attachment:
                return cfdi
            attribute = "registrofiscal:CFDIRegistroFiscal"
            namespace = {"registrofiscal": "http://www.sat.gob.mx/registrofiscal"}
            node = cfdi.Complemento.xpath(attribute, namespaces=namespace)
            if node:
                cfdi.Complemento.remove(node[0])
            with BytesIO(schema) as xsd:
                _check_with_xsd(cfdi, xsd)
            return cfdi
        except ValueError:
            return None
        except OSError:
            return None
        except UserError:
            return None
        except etree.XMLSyntaxError:
            return None
        return None

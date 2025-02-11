# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import _, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.addons.web.controllers.main import clean_action

MX_NS_REFACTORING = {
    "PLZ_": "PLZ",
}

CFDIPLZ_TEMPLATE = "l10n_mx_edi_reports.cfdimoves"
CFDIPLZ_XSD = "l10n_mx_edi_reports/data/xsd/%s/cfdimoves.xsd"
CFDIPLZ_XSLT = "l10n_mx_edi_reports/data/xslt/%s/PolizasPeriodo_1_2.xslt"


class MxReportJournalEntries(models.Model):  # ✅ Changed AbstractModel -> Model
    _inherit = "account.report"  # ✅ Inherit directly
    _description = "Mexican General Ledger Report"

    filter_request_type = "AF"
    filter_order_number = ""
    filter_process_number = ""
    filter_move_name = ""

    def _get_dynamic_report_buttons(self, options):  # ✅ Updated Method
        """Create the buttons to be used to download the required files"""
        buttons = super()._get_dynamic_report_buttons(options)
        buttons.append({"name": _("Export For SAT (XML)"), "action": "print_xml"})
        return buttons

    def _get_columns_name(self, options):  # ✅ Updated for Odoo 17
        return [
            {"name": _("Date"), "class": "date"},
            {"name": _("Acc. Number"), "class": "text"},
            {"name": _("Acc. Name"), "class": "text"},
            {"name": _("Debit"), "class": "number"},
            {"name": _("Credit"), "class": "number"},
        ]

    def _get_table(self, options):  # ✅ Replaces `_get_lines`
        """Fetch table data for report"""
        lines = []
        context = self.env.context
        company_id = context.get("company_id") or self.env.company
        date_from = options["date"].get("date_from")

        # Fetch journal entries grouped by journal_id
        grouped_journals = self.with_context(date_from_aml=date_from).group_by_journal_id(options)

        # Sort and format data for report
        sorted_journals = sorted(grouped_journals, key=lambda j: j.code)
        for journal in sorted_journals:
            if not grouped_journals[journal].get("lines", []):
                continue
            lines.append({
                "id": f"journal_{journal.id}",
                "name": journal.name,
                "columns": [],
                "level": 1,
                "unfoldable": False,
                "unfolded": True,
                "colspan": 6,
            })
            lines.extend(self._get_lines_second_level(options, grouped_journals[journal].get("lines", [])))
        return {"lines": lines}  # ✅ Returns dictionary (Odoo 17 format)

    def _get_lines_second_level(self, options, move_ids):
        lines = []
        moves = move_ids[:80] if len(move_ids) > 80 else move_ids  # ✅ Limit results
        for move in moves:
            name = move.name if len(move.name) <= 35 else move.name[:33] + "..."
            line_id = f"move_{move.id}"
            lines.append({
                "id": line_id,
                "name": name,
                "parent_id": f"journal_{move.journal_id.id}",
                "columns": [{"name": move.date}, {"name": ""}, {"name": ""}, {"name": ""}, {"name": ""}],
                "level": 2,
                "unfoldable": True,
                "unfolded": line_id in options.get("unfolded_lines"),
            })
            if line_id in options.get("unfolded_lines"):
                lines.extend(self._get_lines_third_level(move))
        return lines

    def _get_lines_third_level(self, move):
        lines = []
        basis_account_id = move.company_id.account_cash_basis_base_account_id
        for line in move.line_ids.filtered(lambda l: l.account_id != basis_account_id):
            name = line.name if len(line.name) <= 45 else line.name[:43] + "..."
            lines.append({
                "id": line.id,
                "parent_id": f"move_{move.id}",
                "type": "move_line_id",
                "name": name,
                "columns": [
                    {"name": line.account_id.code},
                    {"name": line.account_id.name},
                    {"name": self.format_value(line.debit)},
                    {"name": self.format_value(line.credit)},
                ],
                "level": 3,
            })
        return lines

    def get_xml(self, options):  # ✅ Updated for Odoo 17
        """Generate XML file"""
        qweb = self.env["ir.qweb"]
        version = "1.3"
        ctx = self._set_context(options)
        ctx["no_format"] = True
        ctx["print_mode"] = True
        values = self.with_context(**ctx).get_bce_dict(options)
        values.update({
            "request_type": options.get("request_type"),
            "order_number": options.get("order_number") or False,
            "process_number": options.get("process_number") or False,
        })
        cfdimoves = qweb.render(CFDIPLZ_TEMPLATE, values)  # ✅ Updated Rendering
        for key, value in MX_NS_REFACTORING.items():
            cfdimoves = cfdimoves.replace(key.encode("UTF-8"), value.encode("UTF-8") + b":")
        cfdimoves = self.l10n_mx_edi_add_digital_stamp(CFDIPLZ_XSLT % version, cfdimoves)
        with tools.file_open(CFDIPLZ_XSD % version, "rb") as xsd:
            _check_with_xsd(cfdimoves, xsd)
        return cfdimoves

    def _get_report_name(self):
        """The structure to name the report is: VAT + YEAR + MONTH + PL"""
        date_report = fields.Date.from_string(self.filter_date.get("date_to")) if self.filter_date.get("date_to") else fields.Date.today()
        return f"{self.env.company.vat or ''}{date_report.year}{str(date_report.month).zfill(2)}PL"

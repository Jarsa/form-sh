from odoo import fields
from odoo.tests import tagged

from odoo.addons.account_reports.tests.common import TestAccountReportsCommon


@tagged("post_install", "post_install_l10n", "-at_install")
class TestAnalyticReport(TestAccountReportsCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref="l10n_mx.mx_coa"):
        super().setUpClass(chart_template_ref=chart_template_ref)

        tag_obj = cls.env["account.analytic.tag"].sudo()
        cls.tag_1 = tag_obj.create({"name": "Tag 1"})
        cls.tag_2 = tag_obj.create({"name": "Tag 2"})
        cls.tag_ids = cls.tag_1 | cls.tag_2

        tax = cls.env.ref(f"l10n_mx.{cls.env.company.id}_tax16")

        date_invoice = "2022-07-01"
        moves_vals = [
            {
                "move_type": "in_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_date": date_invoice,
                "date": date_invoice,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"test {tax.amount}",
                            "quantity": 1,
                            "price_unit": 800,
                            "tax_ids": [(6, 0, tax.ids)],
                            "analytic_tag_ids": [(6, 0, cls.tag_1.ids)],
                        },
                    )
                ],
            },
            {
                "move_type": "in_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_date": date_invoice,
                "date": date_invoice,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"test {tax.amount}",
                            "quantity": 1,
                            "price_unit": 200,
                            "tax_ids": [(6, 0, tax.ids)],
                            "analytic_tag_ids": [(6, 0, cls.tag_2.ids)],
                        },
                    )
                ],
            },
        ]

        moves = cls.env["account.move"].create(moves_vals)
        moves.action_post()

    def test_analytic_report_all_tags_only(self):
        report = self.env["l10n_mx.trial.analytic.report"]

        options = self._init_options(
            report, fields.Date.from_string("2022-01-01"), fields.Date.from_string("2022-12-31")
        )
        headers, lines = report._get_table(options)

        self.assertHeadersValues(
            headers,
            [
                [("", 1), ("2022", 1)],
                [("", 1), ("All Tags", 1)],
            ],
        )
        self.assertLinesValues(
            lines,
            [0, 1],
            [
                ("1 Activos", ""),
                ("119 Impuestos acreditables por pagar", 80.0),
                ("119.01 IVA pendiente de pago", 80.0),
                ("119.01.01 IVA pendiente de pago", 80.0),
                ("Total Activos", 80.0),
                ("2 Pasivos", ""),
                ("201 Proveedores", -1080.0),
                ("201.01 Proveedores nacionales", -1080.0),
                ("201.01.01 Proveedores nacionales", -1080.0),
                ("Total Pasivos", -1080.0),
                ("6 Gastos", ""),
                ("601 Gastos generales", 1000.0),
                ("601.84 Otros gastos generales", 1000.0),
                ("601.84.01 Otros gastos generales", 1000.0),
                ("Total Gastos", 1000.0),
                ("Total", 0),
            ],
        )

    def test_analytic_report_tag_1(self):
        report = self.env["l10n_mx.trial.analytic.report"]

        options = self._init_options(
            report, fields.Date.from_string("2022-01-01"), fields.Date.from_string("2022-12-31")
        )
        options["analytic_tags"] = [self.tag_1.id]

        headers, lines = report._get_table(options)

        self.assertHeadersValues(
            headers,
            [
                [("", 1), ("", 1), ("2022", 1)],
                [("", 1), ("Tag 1", 1), ("All Tags", 1)],
            ],
        )
        self.assertLinesValues(
            lines,
            [0, 1, 2],
            [
                ("1 Activos", "", ""),
                ("119 Impuestos acreditables por pagar", 0.0, 80.0),
                ("119.01 IVA pendiente de pago", 0.0, 80.0),
                ("119.01.01 IVA pendiente de pago", 0.0, 80.0),
                ("Total Activos", 0.0, 80.0),
                ("2 Pasivos", "", ""),
                ("201 Proveedores", 0.0, -1080.0),
                ("201.01 Proveedores nacionales", 0.0, -1080.0),
                ("201.01.01 Proveedores nacionales", 0.0, -1080.0),
                ("Total Pasivos", 0.0, -1080.0),
                ("6 Gastos", "", ""),
                ("601 Gastos generales", 800.0, 1000.0),
                ("601.84 Otros gastos generales", 800.0, 1000.0),
                ("601.84.01 Otros gastos generales", 800.0, 1000.0),
                ("Total Gastos", 800.0, 1000.0),
                ("Total", 800, 0),
            ],
        )

    def test_analytic_report_tags_on_params(self):

        icp_obj = self.env["ir.config_parameter"].sudo()
        icp_obj.set_param("l10n_mx_analytic_reports.analytic_tag_list", self.tag_ids.ids)

        report = self.env["l10n_mx.trial.analytic.report"]

        options = self._init_options(
            report, fields.Date.from_string("2022-01-01"), fields.Date.from_string("2022-12-31")
        )

        headers, lines = report._get_table(options)

        self.assertHeadersValues(
            headers,
            [
                [("", 1), ("", 1), ("", 1), ("2022", 1)],
                [("", 1), ("Tag 1", 1), ("Tag 2", 1), ("All Tags", 1)],
            ],
        )
        self.assertLinesValues(
            lines,
            [0, 1, 2, 3],
            [
                ("1 Activos", "", "", ""),
                ("119 Impuestos acreditables por pagar", 0.0, 0.0, 80.0),
                ("119.01 IVA pendiente de pago", 0.0, 0.0, 80.0),
                ("119.01.01 IVA pendiente de pago", 0.0, 0.0, 80.0),
                ("Total Activos", 0.0, 0.0, 80.0),
                ("2 Pasivos", "", "", ""),
                ("201 Proveedores", 0.0, 0.0, -1080.0),
                ("201.01 Proveedores nacionales", 0.0, 0.0, -1080.0),
                ("201.01.01 Proveedores nacionales", 0.0, 0.0, -1080.0),
                ("Total Pasivos", 0.0, 0.0, -1080.0),
                ("6 Gastos", "", "", ""),
                ("601 Gastos generales", 800.0, 200.0, 1000.0),
                ("601.84 Otros gastos generales", 800.0, 200.0, 1000.0),
                ("601.84.01 Otros gastos generales", 800.0, 200.0, 1000.0),
                ("Total Gastos", 800.0, 200.0, 1000.0),
                ("Total", 800.0, 200.0, 0),
            ],
        )

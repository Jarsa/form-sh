# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class CostMarginUtilityReportWiz(models.TransientModel):
    _name = "cost.margin.utility.report.wiz"
    _description = "Wizard to create cost margin utility reports"

    date_from = fields.Date(
        string="From", required=True, default=fields.Date.context_today
    )
    date_to = fields.Date(
        string="To", required=True, default=fields.Date.context_today
    )

    def open_table(self):
        self.env["cost.margin.utility.report"].search([]).unlink()
        income_accounts = (
            self.env["product.category"]
            .search([])
            .mapped("property_account_income_categ_id")
        )
        expense_accounts = (
            self.env["product.category"]
            .search([])
            .mapped("property_account_expense_categ_id")
        )
        journal_ids = self.env["account.journal"].search([("type", "=", "sale")])
        self._cr.execute(
            """
        SELECT
        table_one.partner_id,
        table_one.quantity,
        table_one.product_id,
        table_one.credit,
        table_one.name,
        table_one.description,
        table_one.categ_id,
        table_one.default_code,
        table_one.id_form,
        table_one.move_id,
        table_two.debit
        FROM
        (
        SELECT
        aml.partner_id,
        aml.quantity,
        aml.product_id,
        aml.credit,
        aml.move_id,
        aml.name,
        pp.default_code,
        pt.id_form,
        pt.description,
        pt.categ_id
        FROM account_move_line aml
        LEFT JOIN account_move am ON aml.move_id = am.id
        LEFT JOIN product_product pp ON aml.product_id = pp.id
        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE
        aml.date BETWEEN %(date_from)s AND %(date_to)s
        AND aml.account_id IN %(income_accounts)s
        AND aml.journal_id IN %(journal_ids)s
        AND am.state = 'posted'
        ) table_one
        LEFT JOIN
        (
        SELECT
        aml2.product_id,
        aml2.debit,
        aml2.move_id
        FROM account_move_line aml2
        LEFT JOIN account_move am2 ON aml2.move_id = am2.id
        WHERE
        aml2.date BETWEEN %(date_from)s AND %(date_to)s
        AND aml2.account_id IN %(expense_accounts)s
        AND aml2.journal_id IN %(journal_ids)s
        AND am2.state = 'posted'
        ) table_two
        ON table_one.move_id = table_two.move_id
        AND table_one.product_id = table_two.product_id
        ;
        """, {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'income_accounts': tuple(income_accounts.ids),
                'expense_accounts': tuple(expense_accounts.ids),
                'journal_ids': tuple(journal_ids.ids),
            }
        )
        query_result = self._cr.dictfetchall()
        report_list = []
        for result in query_result:
            if result.get("credit") > 0:
                quantity = abs(result.get("quantity", 0))
                total_cost = result.get("debit", 0)
                if not quantity or not total_cost:
                    total_cost = 0
                unit_cost = total_cost / quantity
                contribution = result.get("credit") - total_cost
                margin = contribution * 100.0 / result.get("credit")
                report_list.append(
                    {
                        "product_id": result.get("product_id"),
                        "product_category_id": result.get("categ_id"),
                        "product_description": result.get("description"),
                        "sold_qty": quantity,
                        "total_sale": result.get("credit"),
                        "total_cost": total_cost,
                        "unit_cost": unit_cost,
                        "contribution": contribution,
                        "margin": margin,
                        "reference": result.get("name"),
                        "default_code": result.get("default_code"),
                        "form_id": result.get("id_form"),
                        "partner_id": result.get("partner_id"),
                        "move_id": result.get("move_id"),
                    }
                )
        self.env["cost.margin.utility.report"].create(report_list)
        search_view_id = self.env.ref(
            "cost_margin_utility_report.cost_margin_utility_report_search_view"
        ).id
        tree_view_id = self.env.ref(
            "cost_margin_utility_report.cost_margin_utility_report_tree_view"
        ).id
        action = {
            "type": "ir.actions.act_window",
            "name": _("Cost Margin Utility Report"),
            "res_model": "cost.margin.utility.report",
            "view_mode": "tree",
            "search_view_id": search_view_id,
            "views": [[tree_view_id, "list"]],
        }
        return action

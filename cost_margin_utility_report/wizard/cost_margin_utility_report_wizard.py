# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class CostMarginUtilityReportWiz(models.TransientModel):
    _name = "cost.margin.utility.report.wiz"
    _description = "Wizard to create cost margin utility reports"

    date_from = fields.Datetime(
        string="From", required=True, default=fields.Datetime.now
    )
    date_to = fields.Datetime(string="To", required=True, default=fields.Datetime.now)

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
        table_two.debit
        FROM
        (
        SELECT
        aml.partner_id,
        aml.quantity,
        aml.product_id,
        aml.credit,
        aml.move_id,
        am.name,
        pp.default_code,
        pt.id_form,
        pt.description,
        pt.categ_id
        FROM
        account_move_line aml
        INNER JOIN
        account_move am
        ON aml.move_id = am.id
        INNER JOIN
        product_product pp
        ON aml.product_id = pp.id
        INNER JOIN
        product_template pt
        ON pp.product_tmpl_id = pt.id
        WHERE aml.date
        BETWEEN
        %s
        AND
        %s
        AND
        aml.account_id
        IN
        %s
        AND
        aml.journal_id
        IN
        %s) table_one
        INNER JOIN
        (
        SELECT
        product_id,
        debit,
        move_id
        FROM
        account_move_line
        WHERE date
        BETWEEN
        %s
        AND
        %s
        AND
        account_id
        IN
        %s
        AND
        journal_id
        IN
        %s) table_two
        ON table_one.move_id = table_two.move_id
        AND table_one.product_id = table_two.product_id
        ;
        """,
            (
                self.date_from,
                self.date_to,
                tuple(income_accounts.ids),
                tuple(journal_ids.ids),
                self.date_from,
                self.date_to,
                tuple(expense_accounts.ids),
                tuple(journal_ids.ids),
            ),
        )
        query_result = self._cr.dictfetchall()
        report_list = []
        for result in query_result:
            quantity = abs(result["quantity"])
            total_cost = result["debit"]
            unit_cost = total_cost / quantity
            contribution = result["credit"] - total_cost
            margin = contribution * 100.0 / result["credit"]
            report_list.append(
                {
                    "product_id": result["product_id"],
                    "product_category_id": result["categ_id"],
                    "product_description": result["description"],
                    "sold_qty": quantity,
                    "total_sale": result["credit"],
                    "total_cost": total_cost,
                    "unit_cost": unit_cost,
                    "contribution": contribution,
                    "margin": margin,
                    "reference": result["name"],
                    "default_code": result["default_code"],
                    "form_id": result["id_form"],
                    "partner_id": result["partner_id"],
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

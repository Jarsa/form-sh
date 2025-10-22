import ast
from json import loads

from odoo import _, api, models
from odoo.exceptions import UserError


class MxReportAccountAnalyticTrial(models.AbstractModel):
    _name = "l10n_mx.trial.analytic.report"
    _inherit = "l10n_mx.trial.report"
    _description = "Mexican Trial Balance Report"

    filter_hierarchy = None
    filter_comparison = None
    filter_journals = None

    def _get_reports_buttons(self):
        """Create the buttons to be used to download the required files"""
        buttons = [
            {"action": "print_pdf", "file_export_type": "PDF", "name": "Print Preview", "sequence": 1},
            {"action": "print_xlsx", "file_export_type": "XLSX", "name": "Export (XLSX)", "sequence": 2},
        ]
        return buttons

    @api.model
    def _get_columns(self, options):
        icp_obj = self.env["ir.config_parameter"].sudo()
        analytic_obj = self.env["account.analytic.tag"]

        analytic_tag_ids = [tag for tag in options.get("analytic_tags", []) if tag]
        analytic_tag_ids = (
            loads(icp_obj.get_param("l10n_mx_analytic_reports.analytic_tag_list", "[]"))
            if not analytic_tag_ids
            else analytic_tag_ids
        )
        analytic_tag_ids += [False]

        header1 = [{"name": "", "colspan": 1} for x in range(len(analytic_tag_ids))] + [
            {"name": options["date"]["string"], "class": "text-right", "colspan": 1},
        ]

        header2 = [{"name": ""}]

        for analytic_id in analytic_tag_ids:
            analytic = analytic_obj.browse(analytic_id) if analytic_id else analytic_obj
            name = analytic.name_get()[0][1] if analytic else _("All Tags")
            header2.append({"name": name, "class": "number"})

        return [header1, header2]

    @api.model
    def _get_lines(self, options, line_id=None):
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute all sums/unaffected earnings/initial balances for all comparisons.
        icp_obj = self.env["ir.config_parameter"].sudo()

        grouped_accounts = {}
        initial_balances = {}

        analytic_tag_ids = [tag for tag in options.get("analytic_tags", []) if tag]
        analytic_tag_ids = (
            loads(icp_obj.get_param("l10n_mx_analytic_reports.analytic_tag_list", "[]"))
            if not analytic_tag_ids
            else analytic_tag_ids
        )
        analytic_tag_ids += [False]
        comparison_table = analytic_tag_ids

        for analytic_id in analytic_tag_ids:
            new_options = options.copy()
            new_options["unfold_all"] = True
            new_options["analytic_tags"] = [analytic_id] if analytic_id else []

            options_list = self._get_options_periods_list(new_options)
            accounts_results = self.env["account.general.ledger.report.handler"]._do_query(options_list, fetch_lines=False)[0]

            for account, periods_results in accounts_results:
                grouped_accounts.setdefault(account, {}.fromkeys(analytic_tag_ids, 0.0))
                initial_balances.setdefault(account, {}.fromkeys(analytic_tag_ids, 0.0))

                res = periods_results[0]
                account_init_bal = res.get("initial_balance", {})
                initial_balances[account][analytic_id] = account_init_bal.get("balance", 0.0) + res.get(
                    "unaffected_earnings", {}
                ).get("balance", 0.0)
                sums = [
                    res.get("sum", {}).get("debit", 0.0) - account_init_bal.get("debit", 0.0),
                    res.get("sum", {}).get("credit", 0.0) - account_init_bal.get("credit", 0.0),
                ]
                grouped_accounts[account][analytic_id] = initial_balances[account][analytic_id] + sums[0] - sums[1]

        for account, values in grouped_accounts.items():
            grouped_accounts[account] = [values[k] for k in analytic_tag_ids]
        return self._post_process(grouped_accounts, options, comparison_table)

    def _post_process(self, grouped_accounts, options, comparison_table):
        afrl_obj = self.env["account.financial.html.report.line"]
        lines = []
        n_cols = len(comparison_table)
        total = [0.0] * n_cols
        afr_lines = afrl_obj.search([("parent_id", "=", False), ("code", "ilike", "MX_COA_%")], order="code")
        for line in afr_lines:
            childs = self._get_lines_second_level(line.children_ids, grouped_accounts, options, comparison_table)
            if not childs:
                continue
            cols = [""]
            if not options.get("coa_only"):
                cols = cols * n_cols
                child_cols = [c["columns"] for c in childs if c.get("level") == 2]
                total_line = []
                for col in range(n_cols):
                    total_line += [sum(a[col] for a in child_cols)]
                    total[col] += total_line[col]
                for child in childs:
                    child["columns"] = [{"name": self.format_value(v)} for v in child["columns"]]
            lines.append(
                {
                    "id": "hierarchy_" + line.code,
                    "name": line.name,
                    "columns": [{"name": v} for v in cols],
                    "level": 1,
                    "unfoldable": False,
                    "unfolded": True,
                }
            )
            lines.extend(childs)
            if not options.get("coa_only"):
                lines.append(
                    {
                        "id": "total_%s" % line.code,
                        "name": _("Total %s", line.name[2:]),
                        "level": 0,
                        "class": "hierarchy_total",
                        "columns": [{"name": self.format_value(v)} for v in total_line],
                    }
                )
        if not options.get("coa_only"):
            lines.append(
                {
                    "id": "hierarchy_total",
                    "name": _("Total"),
                    "level": 0,
                    "class": "hierarchy_total",
                    "columns": [{"name": self.format_value(v)} for v in total],
                }
            )
        return lines

    @api.model
    def _get_lines_second_level(self, lines_child, grouped_accounts, options, comparison_table):
        """Return list of tags found in the second level"""
        lines = []
        sorted_childs = sorted(lines_child, key=lambda a: a.name)
        for child in sorted_childs:
            account_lines = self._get_lines_third_level(child, grouped_accounts, options, comparison_table)
            if not account_lines:
                continue
            cols = [{"name": ""}]
            if not options.get("coa_only"):
                n_cols = len(comparison_table)
                child_cols = [c["columns"] for c in account_lines if c.get("level") == 3]
                cols = []
                for col in range(n_cols):
                    cols += [sum(a[col] for a in child_cols)]
            lines.append(
                {
                    "id": "level_one_%s" % child.id,
                    "name": child.name,
                    "columns": cols,
                    "level": 2,
                    "class": "hierarchy_total" if not options.get("coa_only") else "",
                    "unfoldable": True,
                    "unfolded": True,
                }
            )
            lines.extend(account_lines)
        return lines

    @api.model
    def _get_lines_third_level(self, line, grouped_accounts, options, comparison_table):
        """Return list of accounts found in the third level"""
        lines = []
        domain = ast.literal_eval(line.domain or "[]")
        domain += [
            ("company_id", "in", self.env.companies.ids),
        ]
        domain.append(("id", "not in", self.env.companies.account_cash_basis_base_account_id.ids))
        account_ids = self.env["account.account"].search(domain, order="code")
        tags = account_ids.mapped("tag_ids").filtered(lambda r: r.color == 4).sorted(key=lambda a: a.name)
        for tag in tags:
            accounts = account_ids.search(
                [
                    ("tag_ids", "in", [tag.id]),
                    ("id", "in", account_ids.ids),
                ]
            )
            name = tag.name
            name = name[:63] + "..." if len(name) > 65 else name
            cols = [{"name": ""}]
            childs = self._get_lines_fourth_level(accounts, grouped_accounts, options, comparison_table)
            if not childs:
                continue
            if not options.get("coa_only"):
                n_cols = len(comparison_table)
                child_cols = [c["columns"] for c in childs]
                cols = []
                for col in range(n_cols):
                    cols += [sum(a[col] for a in child_cols)]
            lines.append(
                {
                    "id": "level_two_%s" % tag.id,
                    "parent_id": "level_one_%s" % line.id,
                    "name": name,
                    "columns": cols,
                    "level": 3,
                    "unfoldable": True,
                    "unfolded": True,
                    "tag_id": tag.id,
                }
            )
            lines.extend(childs)
        return lines

    def _get_lines_fourth_level(self, accounts, grouped_accounts, options, comparison_table):
        lines = []
        company_id = self.env.context.get("company_id") or self.env.company
        is_zero = company_id.currency_id.is_zero
        for account in accounts:
            # skip accounts with all periods = 0 (debit and credit) and no initial balance
            if not options.get("coa_only"):
                non_zero = False
                cols = grouped_accounts.get(account, [])
                if account in grouped_accounts and any(not is_zero(x) for x in cols):
                    non_zero = True
                if not non_zero:
                    continue
            name = account.name_get()[0][1]
            name = name[:63] + "..." if len(name) > 65 else name
            tag = account.tag_ids.filtered(lambda r: r.color == 4)
            if len(tag) > 1:
                raise UserError(_("The account %s is incorrectly configured. Only one tag is allowed."), account.name)
            nature = dict(tag.fields_get()["nature"]["selection"]).get(tag.nature, "")
            cols = [{"name": nature}]
            if not options.get("coa_only"):
                cols = self._get_cols(account, comparison_table, grouped_accounts)
            lines.append(
                {
                    "id": account.id,
                    "parent_id": "level_two_%s" % tag.id,
                    "name": name,
                    "level": 4,
                    "columns": cols,
                    "caret_options": "account.account",
                }
            )
        return lines

    def _get_cols(self, account, comparison_table, grouped_accounts):
        return grouped_accounts[account]

    def _set_context(self, options):
        ctx = super()._set_context(options)
        ctx["model"] = self._name
        return ctx

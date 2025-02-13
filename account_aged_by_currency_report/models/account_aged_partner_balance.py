# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models

class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.report"

    filter_currencies = True

    @api.model
    def _get_options(self, previous_options=None):
        """Update report options to include currency filtering"""
        options = super()._get_options(previous_options=previous_options)
        options['currencies'] = self.env['res.currency'].search([]).read(['name'])
        return options

    @api.model
    def _init_filter_currencies(self, options, previous_options=None):
        """Initialize currency filter"""
        if not self.filter_currencies:
            return
        selected_currency = previous_options and previous_options.get('selected_currency')
        if selected_currency and isinstance(selected_currency, int):
            options['selected_currency_name'] = self.env['res.currency'].browse(selected_currency).name
            options['selected_currency'] = selected_currency
        else:
            options['selected_currency'] = 'company_currency'
            options['selected_currency_name'] = _('Company currency')

    def _query_get(self, options):
        """Build the WHERE clause for account.move.line"""
        tables, where_clause, params = self.env['account.move.line']._query_get(options)
        return f"FROM {tables} WHERE {where_clause}", params

    @api.model
    def _get_sql(self):
        """Construct SQL query for the Aged Partner Balance report"""
        options = self.env.context['report_options']
        selected_currency = options.get('selected_currency')
        
        # Handle currency conversion
        currency_conversion = ""
        if selected_currency and selected_currency != 'company_currency':
            currency_conversion = """
                LEFT JOIN res_currency_rate rate ON rate.currency_id = account_move_line.currency_id
                AND rate.company_id = account_move_line.company_id
                AND rate.name <= %(date)s
                ORDER BY rate.name DESC LIMIT 1
            """

        query = f"""
            SELECT
                account_move_line.id AS line_id,
                account_move_line.partner_id AS partner_id,
                partner.name AS partner_name,
                account_move_line.date_maturity AS due_date,
                account_move_line.balance AS amount_due,
                account_move_line.currency_id AS report_currency_id,
                move.name AS move_name,
                account.name AS account_name,
                {currency_conversion}
            FROM account_move_line
            JOIN account_move move ON move.id = account_move_line.move_id
            JOIN account_account account ON account.id = account_move_line.account_id
            JOIN res_partner partner ON partner.id = account_move_line.partner_id
            {currency_conversion}
            WHERE move.state = 'posted' AND account.internal_type IN ('receivable', 'payable')
            AND account_move_line.currency_id = %(currency_id)s
            ORDER BY account_move_line.date_maturity
        """

        params = {
            'date': options['date']['date_to'],
            'currency_id': selected_currency or self.env.company.currency_id.id,
        }
        
        return self.env.cr.mogrify(query, params).decode(self.env.cr.connection.encoding)

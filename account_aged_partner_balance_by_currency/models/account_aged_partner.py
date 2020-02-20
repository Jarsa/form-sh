# Copyright 2020, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=unidiomatic-typecheck

from odoo import _, api, models
from odoo.tools.misc import format_date


class AccountAgedPartner(models.AbstractModel):
    _inherit = 'account.aged.partner'

    filter_currency_id = True

    @api.model
    def _get_options(self, previous_options=None):
        res = super()._get_options(previous_options)
        if not res.get('currencies', False):
            res['currencies'] = self.env['res.currency'].search(
                []).read(['name'])
        return res

    @api.model
    def _get_lines(self, options, line_id=None):
        if type(options['currency_id']) == int:
            return self._get_lines_2(options, line_id)
        return super()._get_lines(options, line_id)

    @api.model
    def _get_lines_2(self, options, line_id=None):
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        results, total, amls = self.env[
            'report.account.report_agedpartnerbalance'].with_context(
                include_nullified_amount=True)._get_partner_move_lines_2(
                account_types, self._context['date_to'], 'posted', 30,
                options.get('currency_id'))
        for values in results:
            if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                continue
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 3 + [
                    {'name': self.format_value(sign * v)} for v in [
                        values['direction'], values['4'],
                        values['3'], values['2'],
                        values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (
                    values['partner_id'],) in options.get('unfolded_lines'),
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get(
                    'unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    caret_type = 'account.move'
                    if aml.invoice_id:
                        caret_type = (
                            'account.invoice.in' if aml.invoice_id.type in
                            ('in_refund', 'in_invoice') else
                            'account.invoice.out')
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    vals = {
                        'id': aml.id,
                        'name': line_date,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [
                            {'name': v} for v in [
                                aml.journal_id.code, aml.account_id.code,
                                self._format_aml_name(aml)]] + [
                            {'name': v} for v in [
                                line['period'] == 6-i and
                                self.format_value(
                                    sign * line['amount']) or
                                '' for i in range(7)]],
                        'action_context': aml.get_action_context(),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 3 + [
                    {'name': self.format_value(sign * v)} for v in [
                        total[6], total[4], total[3], total[2], total[1],
                        total[0], total[5]]],
            }
            lines.append(total_line)
        return lines

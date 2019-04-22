from odoo import models
from odoo.tools.translate import _


class AccountFollowupReport(models.AbstractModel):

    _inherit = 'account.followup.report'

    def _get_columns_name(self, options):
        res = super()._get_columns_name(options)
        headers = res[:3]
        headers.append({
            'name': _('UUID'),
            'style': 'text-align:center; white-space:nowrap;'
        })
        headers.extend(res[3:])
        return headers

    def _get_lines(self, options, line_id=None):
        lines = super()._get_lines(options, line_id)
        for line in lines:
            # Get all columns available
            invoice_id = line.get('invoice_id', False)
            uuid = {'name': ''}
            if invoice_id:
                invoice = self.env['account.invoice'].browse(invoice_id)
                uuid = {
                    'name': invoice.l10n_mx_edi_cfdi_uuid,
                    'style': 'white-space:nowrap;'
                }
            columns = line['columns'][:2]
            columns.append(uuid)
            columns.extend(line['columns'][2:])
            line['columns'] = columns
        return lines

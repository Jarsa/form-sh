# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.lead'

    timesheet_ids = fields.One2many('account.analytic.line', 'lead_id')
    designer_id = fields.Many2one(
        'res.users',
    )
    first_delivery_date = fields.Date()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get('designer_id', False):
            res.message_subscribe(partner_ids=res.designer_id.partner_id.ids)
        return res

    def write(self, vals):
        if vals.get('designer_id', False):
            user = self.env['res.users'].browse(vals['designer_id'])
            partner_ids = user.partner_id.ids
            self.message_subscribe(partner_ids)
        return super().write(vals)

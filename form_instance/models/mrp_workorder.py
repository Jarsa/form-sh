# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    product_description = fields.Text(related='product_id.description')

    def do_finish(self):
        action = super().do_finish()
        action['domain'] = [
            ('state', 'not in', ['done', 'cancel', 'pending']),
            ('workcenter_id', '=', self.workcenter_id.id),
            ('production_availability', '=', 'assigned'),
        ]
        return action

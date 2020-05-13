# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_mark_done(self):
        for wo in self.workorder_ids:
            if wo.time_ids.filtered(lambda x: (not x.date_end) and (
                    x.loss_type in ('productive', 'performance'))):
                wo.mapped('time_ids').write(
                    {'date_end': fields.Datetime.now()})
        return super().button_mark_done()

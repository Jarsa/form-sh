# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, models


class MRPRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            name = _('%(name)s - %(workcenter)s') % {
                'name': name,
                'workcenter': rec.workcenter_id.name,
            }
            res.append((rec.id, name))
        return res

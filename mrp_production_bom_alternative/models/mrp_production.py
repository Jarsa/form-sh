# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    has_lines_wo_stock = fields.Boolean(
        string='Has Lines Without Stock',
        compute='_compute_has_lines_wo_stock',
        help='Technical field that represents a flag to identify if exists'
        ' a stock move without stock avaliable in the raw moves.',
        copy=False,
    )
    moves_assigned = fields.Boolean(
        string='Raw Moves Assigned',
        help='Technical field used to identify if the user assign'
        ' the raw stock moves.',
        copy=False,
    )

    @api.multi
    @api.depends('move_raw_ids', 'moves_assigned', 'state')
    def _compute_has_lines_wo_stock(self):
        for rec in self:
            stock = (bool(rec.move_raw_ids.filtered(
                lambda m: not m.reserved_availability)) and
                rec.moves_assigned)
            has_bom = (bool(rec.move_raw_ids.filtered(
                lambda m: m.product_id.bom_ids)))
            if has_bom is False:
                if stock is False and rec.state not in (
                        ['confirmed', 'planned']):
                    rec.has_lines_wo_stock = True
                else:
                    rec.has_lines_wo_stock = False
            else:
                rec.has_lines_wo_stock = True

    @api.model
    def create(self, values):
        res = super().create(values)
        res.action_assign()
        return res

    @api.multi
    def action_assign(self):
        for rec in self:
            rec.moves_assigned = True
        return super().action_assign()

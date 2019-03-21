# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class MrpProductionPlan(models.Model):
    _name = 'mrp.production.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production Plan'

    name = fields.Char(readonly=True, copy=False)
    date = fields.Date(required=True, default=fields.Date.context_today)
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        default=lambda self: self.env.user, copy=False)
    request_ids = fields.One2many(
        'mrp.production.request', 'plan_id',
        string='Requests', copy=False, readonly=True,)
    production_ids = fields.One2many(
        'mrp.production', 'plan_id',
        string='Productions', copy=False, readonly=True,)
    line_ids = fields.One2many(
        'mrp.production.plan.line', 'plan_id')
    workcenter_line_ids = fields.One2many(
        'mrp.production.plan.workcenter', 'plan_id')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('approved', 'Approved'),
                   ('planned', 'Planned'),
                   ('done', 'Done'),
                   ('cancel', 'Cancelled')],
        index=True, track_visibility='onchange',
        required=True, copy=False, default='draft')

    @api.multi
    def action_view_productions(self):
        self.ensure_one()
        return {
            'name': _('Manufacturing Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.production_ids.ids)],
            'context': {
                'create': False,
                'delete': False,
                'search_default_status': True,
            }
        }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(
                    force_company=vals['company_id']).next_by_code(
                        'mrp.production.plan') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'mrp.production.plan') or _('New')
        return super().create(vals)

    @api.multi
    def get_mrp_production_requests(self):
        self.ensure_one()
        mrp_plan_line_obj = self.env['mrp.production.plan.line']
        requests = self.env['mrp.production.request'].search([
            ('plan_line_id', '=', False), ('state', '=', 'approved')])
        for request in requests:
            if request in self.line_ids.mapped('request_id'):
                continue
            request.plan_line_id = mrp_plan_line_obj.create({
                'plan_id': self.id,
                'request_id': request.id,
            })
        return True

    @api.multi
    def _sort_workorders_by_sequence(self):
        for wc in self.workcenter_line_ids:
            wc.line_ids.mapped('production_id').button_unplan()
            wc.line_ids.sorted('sequence').mapped(
                'production_id').button_plan()

    @api.multi
    def re_plan(self):
        self.ensure_one()
        pending_lines = self.line_ids.filtered(
            lambda l: l.request_id.state != 'done').sorted(
            'sequence')
        if not pending_lines and self.workcenter_line_ids:
            self._sort_workorders_by_sequence()
        elif pending_lines:
            self.with_context(lines=pending_lines).run_plan()
            for line in pending_lines.mapped('production_id'):
                line.button_plan()
            self._sort_workorders_by_sequence()

    @api.multi
    def link_workorders(self):
        self.ensure_one()
        mrp_plan_wc_obj = self.env['mrp.production.plan.workcenter']
        workcenters = self.production_ids.filtered(
            lambda l: l.workorder_ids).mapped(
                'workorder_ids.workcenter_id')
        for workcenter in workcenters:
            workorders = self.env['mrp.workorder'].search([
                ('workcenter_id', '=', workcenter.id),
                ('production_id', 'in', self.production_ids.ids)])
            old_workcenter = mrp_plan_wc_obj.search([
                ('workcenter_id', '=', workcenter.id),
                ('plan_id', '=', self.id)])
            if old_workcenter:
                old_workcenter.write({
                    'line_ids': [(6, 0, workorders.ids)]
                })
            else:
                mrp_plan_wc_obj.create({
                    'plan_id': self.id,
                    'workcenter_id': workcenter.id,
                    'line_ids': [(6, 0, workorders.ids)]
                })

    @api.multi
    def run_plan(self):
        self.ensure_one()
        wizard_obj = self.env['mrp.production.request.create.mo']
        production_ids = []
        pending_lines = self.line_ids.filtered(
            lambda l: l.request_id.state != 'done').sorted(
            'sequence') if not self._context.get(
                'lines', False) else self._context.get('lines')
        for line in pending_lines:
            wizard = wizard_obj.with_context(
                active_ids=line.request_id.ids,
                active_model='mrp.production.request').create({
                    'mrp_production_request_id': line.request_id.id,
                    'date_planned_start': line.request_id.date_planned_start,
                })
            wizard.compute_product_line_ids()
            # Force the Qty to Produce
            wizard.mo_qty = line.requested_qty
            res = wizard.create_mo()
            res_id = res.get('res_id', False)
            if res_id:
                production_ids.append(res_id)
                line.production_id = res_id
            line.request_id.button_done()
        # Plan the production
        productions = self.env['mrp.production'].browse(production_ids)
        # Write the start and end date
        productions.button_plan()
        for production in productions:
            production.plan_line_id.write({
                'date_planned_start_wo': (
                    production.date_planned_start_wo),
                'date_planned_finished_wo': (
                    production.date_planned_finished_wo),
            })
        self.state = 'planned'
        self.link_workorders()
        return {
            'name': _('Manufacturing Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', production_ids)],
            'context': {
                'create': False,
                'delete': False,
            }
        }

    @api.multi
    def button_approved(self):
        self.write({'state': 'approved'})
        return True

    @api.multi
    def button_done(self):
        self.write({'state': 'done'})
        return True

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True


class MrpProductionPlanLine(models.Model):
    _name = 'mrp.production.plan.line'
    _description = 'Production plan line'

    plan_id = fields.Many2one(
        'mrp.production.plan', string='Plan', required=True, readonly=True)
    request_id = fields.Many2one(
        'mrp.production.request', string='Request',
        required=True, readonly=True)
    product_id = fields.Many2one(
        'product.product', string='Product', related='request_id.product_id',
        readonly=True)
    required_qty = fields.Float(
        readonly=True,
        related='request_id.product_qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    requested_qty = fields.Float(
        string='Requested Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
        default=1.0,
    )
    done_qty = fields.Float(
        string='Done Quantity',
        compute='_compute_done_qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom', string='Unit of Measure',
        readonly=True,
        related="request_id.product_uom_id")
    sequence = fields.Integer(default=10)
    date_planned_start_wo = fields.Datetime(
        'Scheduled Start Date',
    )
    date_planned_finished_wo = fields.Datetime(
        'Scheduled End Date',
    )
    production_id = fields.Many2one(
        'mrp.production',
        string='Manufacture Order',
    )
    planned = fields.Boolean(
        compute='_compute_planned',
        help='Technical field used to identify if the'
        ' manufacture order will be processed',
    )

    @api.multi
    @api.depends('production_id')
    def _compute_done_qty(self):
        for rec in self:
            rec.done_qty = sum(
                rec.production_id.finished_move_line_ids.mapped('qty_done'))

    @api.multi
    @api.depends('production_id')
    def _compute_planned(self):
        for rec in self:
            if not rec.date_planned_finished_wo:
                rec.planned = False
                return True
            start_day = rec.date_planned_start_wo.day
            end_day = rec.date_planned_finished_wo.day
            rec.planned = start_day == end_day

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.request_id.state == 'done':
                raise UserError(_(
                    'You cannot remove a line that has been programmed, you '
                    'need to cancel the Manufacturing Order'))
        return super().unlink()


class MrpProductionPlanWorkcenter(models.Model):
    _name = 'mrp.production.plan.workcenter'
    _description = 'Production plan workcenter'

    workcenter_id = fields.Many2one('mrp.workcenter')
    plan_id = fields.Many2one('mrp.production.plan')
    line_ids = fields.One2many(
        'mrp.workorder', 'plan_workcenter_id', string='Workorder Lines')

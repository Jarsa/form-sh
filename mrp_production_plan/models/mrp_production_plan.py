# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models, tools
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

from datetime import datetime
from dateutil.relativedelta import relativedelta
import math


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
    category_id = fields.Many2one(
        'product.category',
        domain=[('use_in_plan', '=', True)],
        required=True,)
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('approved', 'Approved'),
                   ('planned', 'Planned'),
                   ('done', 'Done'),
                   ('cancel', 'Cancelled')],
        index=True, track_visibility='onchange',
        required=True, copy=False, default='draft')
    finished_orders = fields.Boolean(
        compute='_compute_finished_orders', default=True)
    has_phantom = fields.Boolean(
        readonly=True, compute='_compute_has_phantom',
        help='Technical field used to show or hide columns bom_id and '
        'qty_per_kit if the lines has BoM from Kits.')

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

    @api.depends('production_ids')
    def _compute_finished_orders(self):
        if 'done' not in self.production_ids.mapped('state'):
            self.finished_orders = False

    @api.depends('line_ids')
    def _compute_has_phantom(self):
        if any(self.line_ids.mapped('bom_id')):
            self.has_phantom = True

    @api.model
    def _avoid_duplicate_planned_plans(self, vals):
        existing_plan = self.search([
            ('state', '!=', 'done'),
            ('category_id', '=', vals['category_id'])])
        if existing_plan:
            raise UserError(_(
                'You cannot create a new plan with this category'
                ' if you have not finished a started one.'))

    @api.model
    def create(self, vals):
        self._avoid_duplicate_planned_plans(vals)
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
        main_categ = self.category_id
        product_categories = self._recursive_search_of_categories(main_categ)
        product_categories |= main_categ
        mrp_plan_line_obj = self.env['mrp.production.plan.line']
        requests = self.env['mrp.production.request'].search([
            ('plan_line_id', '=', False), ('state', '=', 'approved'),
            ('product_id.categ_id', 'in', product_categories.ids)])
        for request in requests:
            if request in self.line_ids.mapped('request_id'):
                continue
            request.plan_line_id = mrp_plan_line_obj.create({
                'plan_id': self.id,
                'request_id': request.id,
            })
        return True

    @api.multi
    def _plan_workorders(self, workorders):
        wo_obj = self.env['mrp.workorder']
        if not workorders.mapped('check_ids'):
            workorders._create_checks()
        start_date = datetime.now()
        from_date_set = False
        workorders.write(
            {'date_planned_start': False, 'date_planned_finished': False})
        for workorder in workorders:
            workcenter = workorder.workcenter_id
            wos = wo_obj.search([
                ('workcenter_id', '=', workcenter.id),
                ('date_planned_finished', '!=', False),
                ('plan_workcenter_id.plan_id', '=', self.id),
                ('state', 'in', ('ready', 'pending', 'progress')),
                ('date_planned_finished', '>=',
                    start_date.strftime(
                        tools.DEFAULT_SERVER_DATETIME_FORMAT))],
                order='date_planned_start')
            from_date = start_date
            to_date = workcenter.resource_calendar_id.attendance_ids and (
                workcenter.resource_calendar_id.plan_hours(
                    workorder.duration_expected / 60.0, from_date,
                    compute_leaves=True, resource=workcenter.resource_id))
            if to_date:
                if not from_date_set:
                    # planning 0 hours gives the start of the next attendance
                    from_date = workcenter.resource_calendar_id.plan_hours(
                        0, from_date, compute_leaves=True,
                        resource=workcenter.resource_id)
                    from_date_set = True
            else:
                to_date = from_date + relativedelta(
                    minutes=workorder.duration_expected)
            # Check interval
            for wo in wos:
                if from_date < fields.Datetime.from_string(
                    wo.date_planned_finished) and (
                    to_date > fields.Datetime.from_string(
                        wo.date_planned_start)):
                    from_date = fields.Datetime.from_string(
                        wo.date_planned_finished)
                    to_date = (
                        workcenter.resource_calendar_id.attendance_ids) and (
                        workcenter.resource_calendar_id.plan_hours(
                            workorder.duration_expected / 60.0, from_date,
                            compute_leaves=True,
                            resource=workcenter.resource_id))
                    if not to_date:
                        to_date = from_date + relativedelta(
                            minutes=workorder.duration_expected)
            workorder.write({
                'date_planned_start': from_date,
                'date_planned_finished': to_date})
            if (workorder.operation_id.batch == 'no') or (
                    workorder.operation_id.batch_size >=
                    workorder.qty_production):
                start_date = to_date
            else:
                qty = min(workorder.operation_id.batch_size,
                          workorder.qty_production)
                cycle_number = math.ceil(
                    qty / workorder.production_id.product_qty /
                    workcenter.capacity)
                duration = (
                    workcenter.time_start + cycle_number * (
                        workorder.operation_id.time_cycle * 100.0 /
                        workcenter.time_efficiency))
                to_date = workcenter.resource_calendar_id.attendance_ids and (
                    workcenter.resource_calendar_id.plan_hours(
                        duration / 60.0, from_date, compute_leaves=True,
                        resource=workcenter.resource_id))
                if not to_date:
                    start_date = from_date + relativedelta(minutes=duration)

    @api.multi
    def _sort_workorders_by_sequence(self):
        for wc in self.workcenter_line_ids:
            workorders = wc.line_ids.filtered(
                lambda l: l.state in ['pending', 'ready']).sorted('sequence')
            self._plan_workorders(workorders)

    @api.model
    def _recursive_search_of_categories(self, main_categ):
        categories = self.env['product.category']
        if main_categ.child_id:
            for parent_categ in main_categ.child_id:
                categories |= parent_categ
                if parent_categ.child_id:
                    parent_ids = self._recursive_search_of_categories(
                        parent_categ)
                    for parent_id in parent_ids:
                        categories |= parent_id
        return categories

    @api.model
    def _recursive_search_of_child_orders(self, production):
        productions = self.env['mrp.production']
        pr_child = productions.search([(
            'origin', '=', production.name)])
        if pr_child:
            for child in pr_child:
                productions |= child
                pr_child2 = productions.search([
                    ('origin', '=', child.name)])
                for parent_prod in pr_child2:
                    productions |= parent_prod
                    parent_prod2 = productions.search([
                        ('origin', '=', parent_prod.name)])
                    if parent_prod2:
                        parent_ids = self._recursive_search_of_child_orders(
                            parent_prod)
                        for parent_id in parent_ids:
                            productions |= parent_id
        return productions

    @api.multi
    def re_plan(self):
        self.ensure_one()
        pending_lines = self.line_ids.filtered(
            lambda l: l.request_id.state != 'done').sorted(
            'sequence')
        if not pending_lines and self.workcenter_line_ids:
            self._sort_workorders_by_sequence()
            self._link_workorders()
        elif pending_lines:
            self.with_context(lines=pending_lines).run_plan()
            for line in pending_lines.mapped('production_id'):
                line.button_plan()
            self._sort_workorders_by_sequence()

    @api.multi
    def _link_workorders(self):
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
            child_orders = self._recursive_search_of_child_orders(production)
            for child_order in child_orders:
                child_order.plan_id = self.id
                child_order.button_plan()
            production.plan_line_id.write({
                'date_planned_start_wo': (
                    production.date_planned_start_wo),
                'date_planned_finished_wo': (
                    production.date_planned_finished_wo),
            })
        self.state = 'planned'
        self._link_workorders()
        self._sort_workorders_by_sequence()

    @api.multi
    def button_approved(self):
        self.write({'state': 'approved'})
        return True

    @api.multi
    def button_done(self):
        undone_orders = self.production_ids.filtered(
            lambda x: x.state != 'done')
        if undone_orders:
            for order in undone_orders:
                order.action_cancel()
        unplanned_requests = self.env['mrp.production.request'].search([
            ('origin', 'ilike', 'OP/'), ('plan_line_id', '=', False)])
        if unplanned_requests:
            unplanned_requests.button_cancel()
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
        compute='_compute_requested_qty',
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
        readonly=True,
    )
    date_planned_finished_wo = fields.Datetime(
        'Scheduled End Date',
        readonly=True,
    )
    production_id = fields.Many2one(
        'mrp.production',
        string='Manufacture Order',
        readonly=True,
    )
    planned = fields.Boolean(
        compute='_compute_planned',
        help='Technical field used to identify if the'
        ' manufacture order will be processed',
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string='BoM',
        help='Field used to set the BoM used to compute the quantity per kit.'
    )
    bom_line_ids = fields.Many2many('mrp.bom.line', string='BoM Lines')
    qty_per_kit = fields.Float(readonly=True, default=1.0)
    requested_kit_qty = fields.Float(
        string='Requested Kits',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
        default=0.0,
    )

    @api.multi
    @api.depends('requested_kit_qty')
    def _compute_requested_qty(self):
        for rec in self:
            rec.requested_qty = rec.requested_kit_qty * rec.qty_per_kit

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

    @api.model
    def create(self, values):
        request = self.env['mrp.production.request'].browse(
            values.get('request_id'))
        qty_per_kit = 1.0
        bom_line = request.product_id.bom_line_ids
        if bom_line:
            values.update({
                'bom_line_ids': [(6, 0, bom_line.ids)],
                'bom_id': bom_line[0].bom_id.id,
            })
            qty_per_kit = bom_line[0].product_qty
        values['qty_per_kit'] = qty_per_kit
        return super().create(values)

    @api.multi
    def write(self, vals):
        if vals.get('bom_id'):
            bom = self.env['mrp.bom'].browse(vals.get('bom_id'))
            bom_line = bom.bom_line_ids.filtered(
                lambda l: l.product_id.id == self.product_id.id)
            vals['qty_per_kit'] = bom_line.product_qty
        return super().write(vals)

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        self.qty_per_kit = self.bom_id.bom_line_ids.filtered(
            lambda l: l.product_id.id == self.product_id.id).product_qty


class MrpProductionPlanWorkcenter(models.Model):
    _name = 'mrp.production.plan.workcenter'
    _description = 'Production plan workcenter'

    workcenter_id = fields.Many2one('mrp.workcenter')
    plan_id = fields.Many2one('mrp.production.plan')
    line_ids = fields.One2many(
        'mrp.workorder', 'plan_workcenter_id', string='Workorder Lines')

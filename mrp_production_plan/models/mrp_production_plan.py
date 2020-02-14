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
    _order = 'date desc'

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
    is_planned = fields.Boolean(
        readonly=True, compute='_compute_is_planned',
        help='Technical field used to show or hide columns production_id, and '
        'done_qty if the line is not planned.')
    has_routing = fields.Boolean(
        readonly=True, compute='_compute_has_routing',
        help='Technical field used to show or hide columns '
        'date_planned_start_wo and date_planned_finished_wo if the line don\'t'
        ' have a routing.')
    requests_wo_order = fields.Boolean(
        readonly=True, compute='_compute_requests_wo_order',
        help='Technical field used to show or hide button '
        'done if there are at least one Line (Manufacturing Request) '
        'without a linked Manufacturing Order.')

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

    @api.depends('line_ids')
    def _compute_is_planned(self):
        if any(self.line_ids.mapped('production_id')):
            self.is_planned = True

    @api.depends('line_ids')
    def _compute_has_routing(self):
        if any(self.line_ids.mapped('date_planned_start_wo')):
            self.has_routing = True

    @api.model
    def _avoid_duplicate_planned_plans(self, vals):
        existing_plan = self.search([
            ('state', 'not in', ['done', 'cancel']),
            ('category_id', '=', vals['category_id'])])
        allow_multiple_plans = self.user_has_groups(
            'mrp_production_plan.group_mrp_production_plan_allow_duplicate')
        if not allow_multiple_plans:
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
                ('id', 'in', workorders.ids),
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
                ('production_id', 'in', self.production_ids.ids),
                ('plan_workcenter_id', '=', False)])
            old_workcenter = mrp_plan_wc_obj.search([
                ('workcenter_id', '=', workcenter.id),
                ('plan_id', '=', self.id)])
            if old_workcenter:
                old_workcenter.write({
                    'line_ids': [(4, 0, workorders.ids)]
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
    def _transfer_raw_material(self):
        quant_obj = self.env['stock.quant']
        picking_type = self.env.ref(
            'mrp_production_plan.return_raw_material_form')
        raw_material_categ = self.env.ref(
            '__import__.product_category_002')
        pre_prod_loc = self.env.ref(
            '__export__.stock_location_18_a77b305d')
        stock_loc = self.env.ref(
            '__export__.stock_location_31_2395bc4b')
        products = quant_obj.search([
            ('location_id', '=', pre_prod_loc.id),
            ('product_id.categ_id.id', '=', raw_material_categ.id)]).mapped(
            'product_id')
        products_list = []
        for product in products:
            product_qty = quant_obj._get_available_quantity(
                product_id=product, location_id=pre_prod_loc)
            if not product_qty or product_qty < 0.001:
                continue
            products_list.append((0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': product_qty,
                'product_uom': product.uom_id.id,
                'location_id': pre_prod_loc.id,
                'location_dest_id': stock_loc.id,
            }))
        if not products_list:
            return True
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'move_ids_without_package': products_list,
            'location_id': pre_prod_loc.id,
            'location_dest_id': stock_loc.id,
        })
        picking.action_confirm()
        picking.action_assign()
        validate_picking = picking.button_validate()
        if validate_picking.get('res_id', False):
            wiz = self.env['stock.immediate.transfer'].browse(
                validate_picking['res_id'])
            wiz.process()
            if sum(picking.mapped(
                    'move_line_ids').mapped('product_qty')) != 0.0:
                validate_picking2 = picking.button_validate()
                wiz2 = self.env['stock.backorder.confirmation'].browse(
                    validate_picking2['res_id'])
                wiz2.process_cancel_backorder()

    @api.multi
    def _check_orders_with_partialities(self):
        orders_to_done = self.production_ids.filtered(
            lambda x: x.state not in ('cancel', 'done') and (
                x.finished_move_line_ids) and
            x.availability != 'assigned')
        if orders_to_done:
            orders = ''
            for ordr in orders_to_done:
                orders = orders + '\n-' + ordr.name
            raise UserError(
                _('The following orders have partialities '
                  'and have not been marked as done yet: %s \n')
                % (orders))

    @api.multi
    def _cancel_undone_orders(self):
        workorders = self.production_ids.filtered(
            lambda x: x.state not in ('cancel', 'done') and
            x.availability != 'assigned').mapped(
                'workorder_ids')
        for workorder in workorders:
            workorder.time_ids.unlink()
            workorder.unlink()
        undone_orders = self.production_ids.filtered(
            lambda x: x.state not in ('cancel', 'done') and
            x.availability != 'assigned')
        wrong_orders = undone_orders.filtered(
            lambda w: w.finished_move_line_ids)
        sfp_pickings = self.production_ids.filtered(
            lambda p: p.state == 'done').mapped('picking_ids').filtered(
                lambda p: p.picking_type_id.id == 7 and (
                    p.state in ['assigned', 'confirmed']) and (
                        p.move_line_ids_without_package))
        for line in sfp_pickings.mapped('move_line_ids_without_package'):
            line.qty_done = line.product_uom_qty
        sfp_pickings.split_process()
        empty_pickings = self.env['stock.picking'].search([
            ('backorder_id', 'in', sfp_pickings.ids)])
        empty_pickings.action_cancel()
        if wrong_orders:
            for move_raw in wrong_orders.mapped('move_raw_ids'):
                move_raw.quantity_done = 0.0
            for finished_move in wrong_orders.mapped('finished_move_line_ids'):
                finished_move.qty_done = 0.0
        if undone_orders:
            for order in undone_orders:
                order.action_cancel()

    @api.multi
    def _cancel_unplanned_requests(self):
        unplanned_requests = self.env['mrp.production.request'].search([
            ('plan_line_id', '=', False), '|',
            ('origin', '=', False), ('origin', 'ilike', 'OP/')])
        if unplanned_requests:
            # If a dest move is done the request cannot be cencelled
            unplanned_requests.write({
                'move_dest_ids': False,
            })
            unplanned_requests.button_cancel()

    @api.multi
    def _create_new_requests(self):
        pending_requests = self.request_ids.filtered(
            lambda mr: mr.origin and 'OP' not in mr.origin and (
                mr.pending_qty > 0.0))
        for request in pending_requests:
            new_mr = request.sudo().create({
                'product_id': request.product_id.id,
                'product_qty': request.pending_qty,
                'bom_id': request.bom_id.id,
                'origin': request.origin,
                'product_uom_id': request.product_id.uom_id.id,
            })
            new_mr.button_to_approve()

    @api.multi
    def _cancel_unreserved_moves_to_cedis(self):
        '''This method is created to cancel moves crated by orderpoints that
        are not reserved. If we don't cancel this moves the orderpoint rules
        created the next day it will consider it as vitual stock.

        '''
        sab_stock_loc = self.env.ref('stock.stock_location_stock').id
        transit_loc = self.env.ref('__export__.stock_location_17_4d7ec339').id
        unreserved_moves = self.env['stock.move'].search([
            ('location_id', '=', sab_stock_loc),
            ('location_dest_id', '=', transit_loc),
            ('state', 'in', ('waiting', 'confirmed', 'partially_available'))])
        if unreserved_moves:
            unreserved_moves._action_cancel()

    @api.multi
    def button_done(self):
        self._check_orders_with_partialities()
        self._cancel_undone_orders()
        self._cancel_unplanned_requests()
        self._cancel_unreserved_moves_to_cedis()
        self._transfer_raw_material()
        self._create_new_requests()
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

    @api.multi
    @api.depends('line_ids')
    def _compute_requests_wo_order(self):
        for rec in self:
            if any([not line.production_id for line in rec.line_ids]):
                rec.requests_wo_order = True


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
    order_is_cancel = fields.Boolean(
        compute='_compute_order_is_cancel',
        help='Technical field used to identify if the'
        ' manufacture order will be created again if it was'
        ' cancelled by error.',
    )
    canceled_mo = fields.Boolean(
        compute='_compute_canceled_mo',
        help='Technical field used to identify if there'
        'are cancelled manufacture orders in order to put their'
        'related manufacture request in approved state again ',
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
    @api.depends('production_id')
    def _compute_order_is_cancel(self):
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

    @api.multi
    @api.depends('request_id.mrp_production_ids', 'plan_id.production_ids')
    def _compute_canceled_mo(self):
        for rec in self:
            productions = rec.request_id.mrp_production_ids
            if productions:
                if all([mo.state == 'cancel' for mo in productions]):
                    rec.canceled_mo = True
            else:
                rec.canceled_mo = False

    @api.multi
    def recreate_mo(self):
        for rec in self:
            productions = rec.request_id.mrp_production_ids
            if all([mo.state == 'cancel' for mo in productions]):
                rec.request_id.button_draft()
                rec.request_id.state = 'approved'


class MrpProductionPlanWorkcenter(models.Model):
    _name = 'mrp.production.plan.workcenter'
    _description = 'Production plan workcenter'

    workcenter_id = fields.Many2one('mrp.workcenter')
    plan_id = fields.Many2one('mrp.production.plan')
    line_ids = fields.One2many(
        'mrp.workorder', 'plan_workcenter_id', string='Workorder Lines')

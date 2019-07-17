# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from odoo.tools import float_compare, float_round


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.model
    def create(self, values):
        values['final_lot_id'] = self._get_lot_id(values)
        return super().create(values)

    @api.model
    def _get_lot_id(self, values):
        production = self.env['mrp.production'].browse(values['production_id'])
        if production.product_id.tracking == 'none':
            return False
        if not production.workorder_ids:
            lot = self.env['stock.production.lot'].create({
                'product_id': production.product_id.id,
                'name': self.env['stock.picking']._get_lot_name(self._name)
            })
        else:
            lot = production.workorder_ids.mapped('final_lot_id')
        return lot.id

    def open_tablet_view(self):
        res = super().open_tablet_view()
        last_step = False
        processed_moves = self.env['stock.move.line']
        while not last_step:
            moves = self.move_line_ids.filtered(
                lambda m: m.state not in ('done', 'cancel') and
                m.product_id == self.component_id and
                m not in processed_moves)
            if moves:
                self.write({
                    'lot_id': moves[0].lot_id.id,
                    'qty_done': moves[0].product_qty,
                })
                processed_moves |= moves[0]
            last_step = self.is_last_step
            if not last_step:
                self.action_next()
        return res

    # Copy Odoo method to fix issues with MTS+MTO
    # Odoo created checks and lots calculating the qty required in te bom.line
    # to produce some product, but in MTS+MTO the move is divided in two,
    # Example: You need 550 components of product A and you have 80 in stock,
    # two stock moves were created (1 for 80 and other for 470) but the checks
    # created were for 1100, because it sums every stock.move.
    def _create_checks(self):
        for wo in self:
            # Track components which have a control point
            component_list = []

            production = wo.production_id
            points = self.env['quality.point'].search([
                ('operation_id', '=', wo.operation_id.id),
                ('picking_type_id', '=', production.picking_type_id.id),
                '|', ('product_id', '=', production.product_id.id),
                '&', ('product_id', '=', False),
                ('product_tmpl_id', '=',
                    production.product_id.product_tmpl_id.id)])
            for point in points:
                # Check if we need a quality control for this point
                if point.check_execute_now():
                    if point.component_id:
                        component_list.append(point.component_id.id)
                    moves = wo.move_raw_ids.filtered(
                        lambda m: m.state not in ('done', 'cancel') and
                        m.product_id == point.component_id and
                        m.workorder_id == wo)
                    qty_done = 1.0
                    if (point.component_id and moves and
                            point.component_id.tracking != 'serial'):
                        qty_done = float_round(
                            sum(moves.mapped('unit_factor')),
                            precision_rounding=moves[:1].product_uom.rounding)
                    # Do not generate qc for control point of type
                    # register_consumed_materials if the component is not
                    # consummed in this wo.
                    if not point.component_id or moves:
                        self.env['quality.check'].create({
                            'workorder_id': wo.id,
                            'point_id': point.id,
                            'team_id': point.team_id.id,
                            'product_id': production.product_id.id,
                            # Fill in the full quantity by default
                            'qty_done': qty_done,
                            # Two steps are from the same production
                            # if and only if the produced quantities at the
                            # time they were created are equal.
                            'finished_product_sequence': wo.qty_produced,
                            })

            # Generate quality checks associated with unreferenced components
            move_raw_ids = production.move_raw_ids.filtered(
                lambda m: m.operation_id == wo.operation_id)
            # If last step, add move lines not associated with any operation
            if not wo.next_work_order_id:
                move_raw_ids += production.move_raw_ids.filtered(
                    lambda m: not m.operation_id)
            components = move_raw_ids.mapped('product_id').filtered(
                lambda product: product.tracking != 'none' and
                product.id not in component_list)
            quality_team_id = self.env['quality.alert.team'].search(
                [], limit=1).id
            for component in components:
                moves = wo.move_raw_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel') and
                    m.product_id == component)
                qty_done = 1.0
                if component.tracking != 'serial':
                    qty_done = float_round(
                        sum(moves.mapped('product_qty')),
                        precision_rounding=moves[:1].product_uom.rounding)
                self.env['quality.check'].create({
                    'workorder_id': wo.id,
                    'product_id': production.product_id.id,
                    'component_id': component.id,
                    'team_id': quality_team_id,
                    # Fill in the full quantity by default
                    'qty_done': qty_done,
                    # Two steps are from the same production
                    # if and only if the produced quantities at the time they
                    # were created are equal.
                    'finished_product_sequence': wo.qty_produced,
                })

            # If last step add all the by_product since they are not consumed
            # by a specific operation.
            if not wo.next_work_order_id:
                finished_moves = production.move_finished_ids.filtered(
                    lambda m: not m.workorder_id)
                tracked_by_products = finished_moves.mapped(
                    'product_id').filtered(
                        lambda product: product.tracking != 'none' and
                        product != production.product_id)
                for by_product in tracked_by_products:
                    moves = finished_moves.filtered(
                        lambda m: m.state not in ('done', 'cancel') and
                        m.product_id == by_product)
                    if by_product.tracking == 'serial':
                        qty_done = 1.0
                    else:
                        qty_done = float_round(
                            sum(moves.mapped('product_qty')),
                            precision_rounding=moves[:1].product_uom.rounding)
                    self.env['quality.check'].create({
                        'workorder_id': wo.id,
                        'product_id': production.product_id.id,
                        'component_id': by_product.id,
                        'team_id': quality_team_id,
                        # Fill in the full quantity by default
                        'qty_done': qty_done,
                        'component_is_byproduct': True,
                        # Two steps are from the same production
                        # if and only if the produced quantities at the time
                        # they were created are equal.
                        'finished_product_sequence': wo.qty_produced,
                    })

            # Set default quality_check
            wo.skip_completed_checks = False
            wo._change_quality_check(position=0)

    # Copy Odoo method to fix issues with MTS+MTO
    @api.depends('current_quality_check_id', 'qty_producing')
    def _compute_component_id(self):
        for wo in self.filtered(lambda w: w.state not in ('done', 'cancel')):
            if wo.current_quality_check_id.point_id:
                wo.component_id = (
                    wo.current_quality_check_id.point_id.component_id)
                wo.test_type = wo.current_quality_check_id.point_id.test_type
            elif wo.current_quality_check_id.component_id:
                wo.component_id = wo.current_quality_check_id.component_id
                wo.test_type = 'register_consumed_materials'
            else:
                wo.test_type = ''
            if (wo.test_type == 'register_consumed_materials' and
                    wo.quality_state == 'none'):
                if wo.current_quality_check_id.component_is_byproduct:
                    moves = wo.production_id.move_finished_ids.filtered(
                        lambda m: m.state not in ('done', 'cancel') and
                        m.product_id == wo.component_id)
                else:
                    moves = wo.move_raw_ids.filtered(
                        lambda m: m.state not in ('done', 'cancel') and
                        m.product_id == wo.component_id)
                move = moves[:1]
                lines = wo.active_move_line_ids.filtered(
                    lambda l: l.move_id in moves)
                completed_lines = (
                    lines.filtered(
                        lambda l: l.lot_id) if wo.component_tracking != 'none'
                    else lines)
                wo.component_remaining_qty = float_round(
                    sum(moves.mapped('product_qty')) - sum(
                        completed_lines.mapped('qty_done')),
                    precision_rounding=move.product_uom.rounding)
                wo.component_uom_id = move.product_uom

    # Copy Odoo method to fix issues with MTS+MTO
    def _generate_lot_ids(self):
        """ Generate stock move lines """
        self.ensure_one()
        MoveLine = self.env['stock.move.line']
        tracked_moves = self.move_raw_ids.filtered(
            lambda move: move.state not in ('done', 'cancel') and
            move.product_id.tracking != 'none' and
            move.product_id != self.production_id.product_id and
            move.bom_line_id)
        for move in tracked_moves:
            qty = move.product_qty
            if move.product_id.tracking == 'serial':
                while float_compare(
                        qty, 0.0,
                        precision_rounding=move.product_uom.rounding) > 0:
                    MoveLine.create({
                        'move_id': move.id,
                        'product_uom_qty': 0,
                        'product_uom_id': move.product_uom.id,
                        'qty_done': min(1, qty),
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'product_id': move.product_id.id,
                        'done_wo': False,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                    })
                    qty -= 1
            else:
                MoveLine.create({
                    'move_id': move.id,
                    'product_uom_qty': 0,
                    'product_uom_id': move.product_uom.id,
                    'qty_done': qty,
                    'product_id': move.product_id.id,
                    'production_id': self.production_id.id,
                    'workorder_id': self.id,
                    'done_wo': False,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    })

# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    master_sale_order = fields.Boolean(
        help='If you check this field, this sale order do not run any '
        'procurement and will be selectionable when you request '
        'a product defined in this order.',
    )
    request_id = fields.Many2one(
        comodel_name='sale.request',
        string='Sale Request',
        copy=False,
        readonly=True,
    )

    @api.model
    def create(self, vals):
        if self._context.get('is_master_order'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(
                    force_company=vals['company_id']).next_by_code(
                        'master.sale.order') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'master.sale.order') or _('New')
        return super().create(vals)

    def action_cancel(self):
        for rec in self:
            if rec.master_sale_order and any(
                    [line.child_ids for line in self.order_line]):
                raise UserError(
                    _('Error!, You can not cancel a sale order when the sale'
                      ' order lines has child lines generated '
                      'from sale requests.'))
        return super().action_cancel()

    def button_link_sale_order(self):
        return {
            'name': _('Link sale order'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'link.sale.order.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def button_child_sale_orders(self):
        self.ensure_one()
        order_ids = self.order_line.mapped('child_ids.order_id').ids
        return {
            'name': _('Sale orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', order_ids)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
            },
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    master_sale_order = fields.Boolean(
        related='order_id.master_sale_order',
        help='If you check this field, this sale order do not run any '
        'procurement and will be selectionable when you request '
        'a product defined in this order.',
    )
    parent_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Parent Sale Order Line',
        copy=False,
        readonly=True,
        help='Parent sale order line (master sale order).'
    )
    child_ids = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='parent_id',
        string='Child Sale Order Lines',
        copy=False,
        readonly=True,
        help='Sale Order Lines generated by sale request linked to this line.'
    )
    request_line_id = fields.Many2one(
        comodel_name='sale.request.line',
        string='Sale Request',
        copy=False,
        ondelete='restrict',
    )
    product_uom_qty_total = fields.Float(
        string='Total Ordered Quantity',
        copy=False,
        compute='_compute_product_uom_qty_total',
        compute_sudo=True,
        store=True,
        digits='Product Unit of Measure',
    )
    qty_delivered_total = fields.Float(
        string='Total Delivered Quantity',
        copy=False,
        compute='_compute_qty_delivered_total',
        compute_sudo=True,
        store=True,
        digits='Product Unit of Measure',
    )
    qty_invoiced_total = fields.Float(
        string='Total Invoiced Quantity',
        copy=False,
        compute='_compute_qty_invoiced_total',
        compute_sudo=True,
        store=True,
        digits='Product Unit of Measure',
    )
    remaining_product_qty = fields.Float(
        string='Remaining Product quantity',
        copy=False,
        compute='_compute_remaining_product_qty',
        compute_sudo=True,
        store=True,
        digits='Product Unit of Measure',
    )

    def write(self, values):
        name_user = self.env.user.name
        fields_blocked = ['product_uom_qty', 'price_unit', 'tax_id']
        if not self.user_has_groups(
                'sale_request.group_edit_sale_order_line_price'):
            for rec in fields_blocked:
                if rec in values:
                    raise UserError(
                        _('The user %s can not permission to edit the price'
                            'unit, quantity and taxes') % name_user)
        return super().write(values)

    @api.depends('product_type', 'product_uom_qty', 'qty_delivered', 'state', 'move_ids', 'product_uom')
    def _compute_qty_to_deliver(self):
        if not self.order_id.master_sale_order:
            return super()._compute_qty_to_deliver()

    @api.depends('child_ids.product_uom_qty', 'child_ids.order_id.state')
    def _compute_product_uom_qty_total(self):
        for rec in self:
            rec.product_uom_qty_total = sum(rec.child_ids.filtered(
                lambda l: l.order_id.state not in 'cancel').mapped(
                'product_uom_qty'))

    @api.depends('product_uom_qty', 'product_uom_qty_total')
    def _compute_remaining_product_qty(self):
        for rec in self:
            rec.remaining_product_qty = (
                rec.product_uom_qty - rec.product_uom_qty_total)

    @api.depends('child_ids.qty_delivered', 'child_ids.order_id.state')
    def _compute_qty_delivered_total(self):
        for rec in self:
            rec.qty_delivered_total = sum(rec.child_ids.filtered(
                lambda l: l.order_id.state not in 'cancel').mapped(
                'qty_delivered'))

    @api.depends('child_ids.qty_invoiced', 'child_ids.order_id.state')
    def _compute_qty_invoiced_total(self):
        for rec in self:
            rec.qty_invoiced_total = sum(rec.child_ids.filtered(
                lambda l: l.order_id.state not in 'cancel').mapped(
                'qty_invoiced'))

    def _action_launch_stock_rule(self):
        """Method overrided from odoo to avoid the launching for the
        stock rules when a sale order is a master sale order"""
        if all([order.master_sale_order for order in self.mapped('order_id')]):
            return True
        return super()._action_launch_stock_rule()

# -*- coding: utf-8 -*-
# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# pylint: disable=attribute-string-redundant,except-pass

from odoo import _, api, fields, models
from odoo.tools import float_compare
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    request_line_id = fields.Many2one(
        'sale.request.line',
        string='Sale Request Line',
        ondelete='set null',
        copy=False,
    )


class SaleRequest(models.Model):
    _name = 'sale.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Request'
    _order = 'date desc, id desc'

    name = fields.Char(
        required=True,
        readonly=True,
        default="/",
        copy=False,
    )
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        domain=[('category_id', 'in', [1])],
    )

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('done', 'Terminado'),
        ('cancel', 'Cancelado')],
        default='draft',
        required=True,
        readonly=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    requested_by = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        required=True,
        readonly=True,
        tracking=True,
    )
    description = fields.Text()
    line_ids = fields.One2many(
        'sale.request.line',
        'request_id',
        string='Lines',
        copy=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        related='line_ids.product_id',
        readonly=False,
        help='Field used to search sale requests by product',
    )
    sale_ids = fields.Many2many(
        'sale.order',
        compute='_compute_sale_ids',
        string='Sales',
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
    )
    route_id = fields.Many2one(
       'stock.route',
        string='Route',
        domain=[('sale_selectable', '=', True)],
        ondelete='restrict',
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Shipping Address',
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per Company!'),
    ]

    @api.depends('line_ids.sale_line_ids.order_id')
    def _compute_sale_ids(self):
        for rec in self:
            rec.sale_ids = rec.line_ids.mapped('sale_line_ids.order_id')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.partner_shipping_id = (
            self.partner_id.child_ids
                .filtered(lambda p: p.type == 'delivery')[:1]
            or self.partner_id
        )

    @api.model
    def _create_sequence(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.request') or '/'
        return vals

    @api.model
    def create(self, vals):
        vals = self._create_sequence(vals)
        rec = super().create(vals)
        rec._subscribe_assigned_user(vals)
        return rec

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._subscribe_assigned_user(vals)
        return res

    def _subscribe_assigned_user(self, vals):
        self.ensure_one()
        if vals.get('assigned_to'):
            self.message_subscribe(partner_ids=[self.assigned_to.id])

    def button_draft(self):
        return self.write({'state': 'draft'})

    def button_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('You can only confirm draft sale requests.'))
        self.write({'state': 'confirm'})

    def button_cancel(self):
        self.ensure_one()
        if self.line_ids.filtered(lambda l: l.sale_line_ids and l.sale_line_ids.state == 'sale'):
            raise UserError(_('You cannot cancel a sale request linked to confirmed sale orders.'))
        self.write({'state': 'cancel'})

    def button_sale_request_lines(self):
        return {
            'name': _('Sale request lines'),
            'view_mode': 'tree,form',
            'res_model': 'sale.request.line',
            'domain': [('id', 'in', self.line_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
        }

    def button_sale_orders(self):
        self.ensure_one()
        orders = self.line_ids.mapped('sale_line_ids.order_id')
        return {
            'name': _('Sale Orders'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', orders.ids)],
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False, 'is_master_order': False},
        }


class SaleRequestLine(models.Model):
    _name = 'sale.request.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Request Line'
    display_name = fields.Char(
        string='Name', 
        compute='_compute_display_name',
        store=False,
    )

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name_get()[0][1]
    request_id = fields.Many2one(
        'sale.request',
        string='Sale Request',
        ondelete='cascade',
        copy=False,
    )
    request_state = fields.Selection(
        related='request_id.state',
        string='Request State',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('sale_ok', '=', True)],
    )
    description = fields.Text()
    product_qty = fields.Float(
        string="Required Quantity",
        required=True,
        digits='Product Unit of Measure',
        default=1.0,
        tracking=True,         # <— ejemplo de seguimiento
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
        domain="[('category_id','=',category_uom_id)]",
    )
    category_uom_id = fields.Many2one(
        related='product_uom_id.category_id',
    )
    sale_line_ids = fields.One2many(
        'sale.order.line',
        'request_line_id',
        string='Sale Order Lines',
        copy=False,
    )
    remaining_product_qty = fields.Float(
        string="Remaining Quantity",
        digits='Product Unit of Measure',
        compute='_compute_remaining_product_qty',
        store=True,
    )
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('done', 'Completado')],
        default='pending',
        readonly=True,
        required=True,
    )

    @api.depends('product_qty', 'sale_line_ids.product_uom_qty', 'sale_line_ids.order_id.state')
    def _compute_remaining_product_qty(self):
        for rec in self:
            delivered = sum(
                line.product_uom._compute_quantity(line.product_uom_qty, rec.product_uom_id)
                for line in rec.sale_line_ids.filtered(lambda l: l.order_id.state != 'cancel')
            )
            rec.remaining_product_qty = rec.product_qty - delivered

    def unlink(self):
        for rec in self:
            if rec.sale_line_ids:
                raise UserError(_(
                    'You cannot delete a request line that is already linked '
                    'to a Sale Order'))
        return super().unlink()

    def name_get(self):
        return [
            (rec.id, '[%s] %s' % (rec.request_id.name, rec.product_id.display_name))
            for rec in self
        ]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self._onchange_product_id_check_availability()
        self.product_uom_id = self.product_id.uom_id
        self.description = self.product_id.get_product_multiline_description_sale()

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        self._onchange_product_id_check_availability()

    @api.onchange('product_id', 'product_qty')
    def _onchange_product_id_check_availability(self):
        if not (self.product_id and self.product_qty) or self.request_id.route_id:
            return
        if self.product_id.type == 'product':
            comps = []
            products_to_check = self._recursive_search_of_components(self.product_id.bom_ids, comps)
            if products_to_check:
                self._check_availability_kit_bom(products_to_check)
            else:
                self._check_availability_normal_bom(self.product_id)

    def _check_availability_normal_bom(self, product):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        prod = product.with_context(
            warehouse=self.request_id.warehouse_id.id,
            lang=self.request_id.partner_id.lang or self.env.user.lang or 'en_US'
        )
        qty = product.uom_id._compute_quantity(self.product_qty, product.uom_id)
        if float_compare(prod.virtual_available, qty, precision_digits=precision) < 0:
            if not self._check_routing():
                msg = _(
                    'You plan to sell %(needed)s %(uom)s of %(prod)s but only '
                    '%(avail)s %(uom)s available in %(wh)s.'
                ) % {
                    'needed': self.product_qty,
                    'uom': product.uom_id.name,
                    'prod': product.display_name,
                    'avail': prod.virtual_available,
                    'wh': self.request_id.warehouse_id.name,
                }
                raise UserError(_('Not enough inventory!\n%s') % msg)

    def _check_availability_kit_bom(self, products_to_check):
        missing = []
        for comp in products_to_check:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            prod = comp['product_id'].with_context(warehouse=self.request_id.warehouse_id.id)
            required = comp['product_qty'] * self.product_qty
            if float_compare(prod.virtual_available, required, precision_digits=precision) < 0:
                missing.append((prod, required, prod.virtual_available))
        if missing:
            details = "\n".join(
                "%s: needed %s, available %s" % (p.display_name, need, avail)
                for p, need, avail in missing
            )
            raise UserError(_('Not enough kit components:\n%s') % details)

    def _recursive_search_of_components(self, boms, products):
        for bom in boms.filtered(lambda b: b.type == 'phantom'):
            for line in bom.bom_line_ids:
                if line.product_id.bom_ids.filtered(lambda b: b.type == 'phantom'):
                    self._recursive_search_of_components(line.product_id.bom_ids, products)
                else:
                    products.append({'product_id': line.product_id, 'product_qty': line.product_qty})
        return products

    def _check_routing(self):
        routes = self.product_id.route_ids + self.product_id.categ_id.total_route_ids
        wh = self.request_id.warehouse_id
        mto = wh.mto_pull_id.route_id
        if mto and mto in routes:
            return True
        try:
            default_mto = self.env['stock.warehouse']._find_global_route(
                'stock.route_warehouse0_mto', _('Make To Order'))
            if default_mto in routes:
                return True
        except UserError:
            pass
        # drop-shipping
        for rule in routes.mapped('rule_ids'):
            pt = rule.picking_type_id.sudo()
            if pt.default_location_src_id.usage == 'supplier' and pt.default_location_dest_id.usage == 'customer':
                return True
        return False

    def button_sale_orders(self):
        self.ensure_one()
        orders = self.sale_line_ids.mapped('order_id')
        return {
            'name': _('Sale Orders'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', orders.ids)],
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False, 'is_master_order': False},
        }

    def button_open_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.sale.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'active_model': 'sale.request.line',
            },
        }

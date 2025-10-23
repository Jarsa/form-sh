# -*- coding: utf-8 -*-
# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LinkSaleOrderWizard(models.TransientModel):
    _name = 'link.sale.order.wizard'
    _description = 'Link Sale Orders with Master Sale Order'
    order_id      = fields.Many2one('sale.order', string='Master Order', readonly=True)
    partner_id    = fields.Many2one('res.partner',     string='Customer', readonly=True)
    line_ids      = fields.One2many(
        'link.master.sale.order.wizard.line', 'wizard_id',
        string='Master Sale Order Lines',
    )
    sale_line_ids = fields.Many2many('sale.order.line', string='Lines with no link')
    product_ids   = fields.Many2many('product.product', string='Products',     readonly=True)

    def _prepare_item(self, line):
        return {
            'sale_line_id':          line.id,
            'product_id':            line.product_id.id,
            'remaining_product_qty': line.remaining_product_qty,
            'name':                  line.name,
            'product_uom_qty':       line.product_uom_qty,
            'product_uom_id':        line.product_uom.id,
        }

    @api.onchange('sale_line_ids')
    def _onchange_sale_line_ids(self):
        # si no estamos en singleton o no hay selección, salimos
        if len(self) != 1 or not self.sale_line_ids:
            return
        try:
            for wiz_line in self.line_ids:
                total = 0
                sel = self.sale_line_ids.filtered(
                    lambda l: l.product_id == wiz_line.product_id)
                for ln in sel:
                    total += ln.product_uom._compute_quantity(
                        ln.product_uom_qty, wiz_line.product_uom_id)
                total += sum(wiz_line.sale_line_id.child_ids.mapped('product_uom_qty'))
                wiz_line.remaining_product_qty = wiz_line.product_uom_qty - total
        except ValueError:
            # Capturamos cualquier expected singleton interno y abortamos
            return

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self._context.get('active_id')
        if not active_id:
            return res
        order = self.env['sale.order'].browse(active_id)
        # Rellenamos el nuevo campo order_id:
        res['order_id']    = active_id
        res['partner_id']  = order.partner_id.id
        res['product_ids'] = [(6, 0, order.order_line.mapped('product_id').ids)]
        # Creamos las líneas wizard de las que tienen qty pendiente:
        wiz_lines = []
        for line in order.order_line.filtered(lambda l: l.remaining_product_qty > 0):
            wiz_lines.append((0, 0, {
                'sale_line_id':          line.id,
                'product_id':            line.product_id.id,
                'remaining_product_qty': line.remaining_product_qty,
                'name':                  line.name,
                'product_uom_qty':       line.product_uom_qty,
                'product_uom_id':        line.product_uom.id,
            }))
        res['line_ids'] = wiz_lines
        return res

    def link_sale_order(self):
        self.ensure_one()
        linked_orders = []
        for wiz_line in self.line_ids:
            sel = self.sale_line_ids.filtered(
                lambda l: l.product_id == wiz_line.product_id)
            orders = sel.mapped('order_id')
            for ord in orders:
                ref = wiz_line.sale_line_id.order_id.client_order_ref or ''
                if ord.client_order_ref and ord.client_order_ref != ref:
                    ref = '%s | %s' % (ord.client_order_ref, ref)
                ord.client_order_ref = ref
            sel.write({'parent_id': wiz_line.sale_line_id.id})
            linked_orders += orders.ids

        return {
            'name': _('Sale Orders'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', linked_orders)],
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
        }


class LinkSaleOrderWizardLine(models.TransientModel):
    _name = 'link.master.sale.order.wizard.line'
    _description = 'Lines of Master Sale Order'

    wizard_id             = fields.Many2one('link.sale.order.wizard', readonly=True)
    sale_line_id          = fields.Many2one('sale.order.line',        readonly=True)
    product_id            = fields.Many2one('product.product',        readonly=True)
    name                  = fields.Text(readonly=True)
    product_uom_qty       = fields.Float(digits='Product Unit of Measure', readonly=True)
    remaining_product_qty = fields.Float(digits='Product Unit of Measure', readonly=True)
    product_uom_id        = fields.Many2one('uom.uom',                readonly=True)

    @api.model
    def _prepare_line(self, line):
        return {
            'sale_line_id':    line.id,
            'product_id':      line.product_id.id,
            'name':            line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom_id':  line.product_uom.id,
        }

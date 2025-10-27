# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateSaleOrderWizard(models.TransientModel):
    _name = 'create.sale.order.wizard'
    _description = 'Create Sale Orders From Sale Request'

    line_ids               = fields.One2many('create.sale.order.wizard.line', 'wizard_id', string='Proposed Sale Order Lines')
    request_line_id        = fields.Many2one('sale.request.line',      string='Sale Request Line')
    product_id             = fields.Many2one('product.product',        readonly=True)
    product_qty            = fields.Float(readonly=True, digits='Product Unit of Measure')
    product_uom_id         = fields.Many2one('uom.uom',                readonly=True)
    remaining_product_qty  = fields.Float(readonly=True, digits='Product Unit of Measure')
    has_lines              = fields.Boolean(compute='_compute_has_lines')
    on_time                = fields.Boolean(default=lambda self: self._compute_on_time())
    confirm_without_master = fields.Boolean(string='Confirm without Master Sale Order')

    def _compute_on_time(self):
        now     = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        current = now.hour * 60 + now.minute
        start   = int(self.env['ir.config_parameter'].sudo().get_param('sale_request_time_start', 0)) * 60
        end     = int(self.env['ir.config_parameter'].sudo().get_param('sale_request_time_end', 24)) * 60
        return start <= current <= end

    @api.depends('line_ids')
    def _compute_has_lines(self):
        for w in self:
            w.has_lines = bool(w.line_ids)

    @api.onchange('line_ids')
    def _onchange_qty_to_sale(self):
        if not self.line_ids:
            return
        rem  = self.request_line_id.remaining_product_qty
        used = sum(self.line_ids.mapped('qty_to_sale'))
        if used > rem:
            self.remaining_product_qty = rem
            return {
                'warning': {
                    'title': _('Error!'),
                    'message': _('You cannot request more than the initial demand.'),
                },
            }
        self.remaining_product_qty = rem - used

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self._context.get('active_id')
        if not active_id:
            return res
        req_line = self.env['sale.request.line'].browse(active_id)
        domain = [
            ('state', '=', 'sale'),
            ('product_id', '=', req_line.product_id.id),
            ('order_id.master_sale_order', '=', True),
            ('remaining_product_qty', '>', 0.0),
            ('order_id.partner_id', '=', req_line.request_id.partner_id.id),
        ]
        wiz = []
        for line in self.env['sale.order.line'].search(domain):
            wiz.append((0, 0, {
                'product_id':            line.product_id.id,
                'name':                  line.name,
                'product_uom_qty':       line.product_uom_qty,
                'product_uom_id':        line.product_uom.id,
                'order_id':              line.order_id.id,
                'sale_line_id':          line.id,
                'remaining_product_qty': line.remaining_product_qty,
                'qty_to_sale':           0,
            }))
        res.update({
            'request_line_id':       req_line.id,
            'product_id':            req_line.product_id.id,
            'product_qty':           req_line.product_qty,
            'product_uom_id':        req_line.product_uom_id.id,
            'remaining_product_qty': req_line.remaining_product_qty,
            'line_ids':              wiz,
        })
        return res

    @api.model
    def _get_pricelist_id(self, request_line, sale_line):
        if sale_line:
            return sale_line.order_id.pricelist_id.id
        partner   = request_line.request_id.partner_id
        pricelist = partner.property_product_pricelist
        if not pricelist:
            raise UserError(_('Customer %s has no pricelist.') % partner.name)
        return pricelist.id

    @api.model
    def _prepare_sale_order(self, request, sale_line_id, pricelist_id):
        partner = request.partner_id
        fpos    = partner.property_account_position_id
        return {
            'partner_id':         partner.id,
            'user_id':            self.env.user.id,
            'company_id':         request.company_id.id,
            'date_order':         fields.Datetime.now(),
            'client_order_ref':   sale_line_id and sale_line_id.order_id.client_order_ref or False,
            'origin':             request.name,
            'warehouse_id':       request.warehouse_id.id,
            'request_id':         request.id,
            'fiscal_position_id': fpos.id if fpos else False,
            'pricelist_id':       pricelist_id,
            'payment_term_id':    partner.property_payment_term_id.id,
            'partner_shipping_id': request.partner_shipping_id.id,
            # enlaza la orden hija con el master
            'master_order_id':    sale_line_id and sale_line_id.order_id.id or False,
        }

    @api.model
    def _get_sale_order(self, request_line, sale_line=False):
        pricelist_id = self._get_pricelist_id(request_line, sale_line)
        SaleOrder = self.env['sale.order']
        domain = [
            ('request_id', '=', request_line.request_id.id),
            ('pricelist_id', '=', pricelist_id),
            ('master_order_id','=', sale_line and sale_line.order_id.id or False),
        ]
        order = SaleOrder.search(domain, limit=1)
        if not order:
            order = SaleOrder.create(self._prepare_sale_order(
                request_line.request_id, sale_line, pricelist_id))
        return order

    def _prepare_sale_order_line(self, order, params):
        req_line = self.request_line_id
        product  = req_line.product_id
        taxes    = product.taxes_id
        if order.fiscal_position_id:
            # map_tax ahora recibe sólo la lista de taxes
            taxes = order.fiscal_position_id.map_tax(taxes)
        price = (params.get('sale_line_id')
                 and self.env['sale.order.line'].browse(params['sale_line_id']).price_unit
                 or product.lst_price)
        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            price, taxes, taxes, self.env.user.company_id)
        return {
            'product_id':      product.id,
            'product_uom_qty': params['qty_to_sale'],
            'product_uom':     params['product_uom'],  # <- clave CORRECTA
            'request_line_id': req_line.id,
            'route_id':        req_line.request_id.route_id.id or False,
            'parent_id':       params.get('sale_line_id'),
            'order_id':        order.id,
            'tax_id':          [(6, 0, taxes.ids)],
            'price_unit':      price_unit,
        }

    def create_sale_order(self):
        self.ensure_one()
        so_set = self.env['sale.order']
        sol    = self.env['sale.order.line']
        req    = self.request_line_id.sudo()

        # 1) Caso sin master: creamos una única orden hija
        if not self.line_ids or self.confirm_without_master:
            order = self._get_sale_order(req, False)
            so_set |= order
            sol.create(self._prepare_sale_order_line(order, {
                'qty_to_sale':  req.remaining_product_qty,
                'product_uom':  req.product_uom_id.id,   # <- aquí también
                'sale_line_id': False,
            }))
            req.remaining_product_qty = 0

        # 2) Con master: tantas órdenes hijas como líneas marcadas
        else:
            for ln in self.line_ids.filtered('qty_to_sale'):
                order = self._get_sale_order(req, ln.sale_line_id)
                so_set |= order
                sol.create(self._prepare_sale_order_line(order, {
                    'qty_to_sale':  ln.qty_to_sale,
                    'product_uom':  ln.product_uom_id.id,   # <- y aquí
                    'sale_line_id': ln.sale_line_id.id,
                }))

        # **Forzamos** el state = 'sale' directo (sin pasar por cotización)
        if so_set:
            so_set.write({'state': 'sale'})

        # Cerrar request line / request padre si toca
        if req.remaining_product_qty == 0:
            req.state = 'done'
            parent_req = req.request_id
            if not parent_req.line_ids.filtered(lambda l: l.state != 'done'):
                parent_req.state = 'done'

        # Mostrar la(s) orden(es) resultante(s)
        if len(so_set) > 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'tree,form',
                'domain': [('id','in',so_set.ids)],
                'context': {'create': False, 'delete': False},
            }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': so_set.id,
            'context': {'create': False, 'delete': False},
        }


class CreateSaleOrderWizardLine(models.TransientModel):
    _name = 'create.sale.order.wizard.line'
    _description = 'Lines to Create Sale Orders From Sale Request'

    wizard_id              = fields.Many2one('create.sale.order.wizard', ondelete='cascade')
    order_id               = fields.Many2one('sale.order',   readonly=True)
    sale_line_id           = fields.Many2one('sale.order.line')
    product_id             = fields.Many2one('product.product', readonly=True)
    name                   = fields.Text()
    product_uom_qty        = fields.Float(digits='Product Unit of Measure')
    remaining_product_qty  = fields.Float(digits='Product Unit of Measure')
    product_uom_id         = fields.Many2one('uom.uom', related='sale_line_id.product_uom')
    qty_to_sale            = fields.Float(digits='Product Unit of Measure')

    @api.onchange('qty_to_sale')
    def _onchange_qty_to_sale(self):
        if self.qty_to_sale:
            rem = self.sale_line_id.remaining_product_qty
            if self.qty_to_sale > rem:
                self.remaining_product_qty = rem
                return {
                    'warning': {
                        'title': _('Error!'),
                        'message': _('Cannot request more than remaining qty.')
                    }
                }
            self.remaining_product_qty = rem - self.qty_to_sale

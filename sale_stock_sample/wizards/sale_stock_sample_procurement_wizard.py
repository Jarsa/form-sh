# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleStockSampleProcurementWizard(models.TransientModel):
    _name = 'sale.stock.sample.procurement.wizard'
    _description = 'Create Procurement for Sample Products'

    route_id = fields.Many2one(
        comodel_name='stock.location.route',
        string='Route',
        domain=[('sample_selectable', '=', True)],
        help='Define the route to generate the procurement for each product.',
    )
    line_ids = fields.One2many(
        comodel_name='sale.stock.sample.procurement.wizard.line',
        inverse_name='wizard_id',
        string='Lines to Procure',
    )

    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id:
            self.line_ids.update({
                'route_id': self.route_id.id,
            })

    @api.model
    def _prepare_item(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'order_id': line.order_id.id,
            'sale_line_id': line.id,
        }

    @api.model
    def default_get(self, res_fields):
        res = super().default_get(res_fields)
        order = self.env['sale.order'].browse(
            self._context.get('active_ids'))
        order_lines = order.order_line.filtered(
            lambda l: l.product_id.type in ('consu', 'product'))
        lines = []
        for line in order_lines:
            lines.append((0, 0, self._prepare_item(line)))
        res['line_ids'] = lines
        return res

    @api.multi
    def run_procurements(self):
        self.ensure_one()
        self.line_ids._action_launch_stock_rule()
        return True


class SaleStockSampleProcurementLineWizard(models.TransientModel):
    _name = 'sale.stock.sample.procurement.wizard.line'
    _description = 'Lines to Create Procurement for Sample Products'

    wizard_id = fields.Many2one(
        comodel_name='sale.stock.sample.procurement.wizard',
        string='Wizard',
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
    )
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Line',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Text(
        string="Description",
    )
    product_uom_qty = fields.Float(
        string='Ordered Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
    )
    date_planned = fields.Date(
        default=fields.Date.today,
        help='Define the estimated date to deliver the sample product.',
    )
    route_id = fields.Many2one(
        comodel_name='stock.location.route',
        string='Route',
        domain=[('sample_selectable', '=', True)],
        help='Define the route to generate the procurement for each product.',
    )
    qty_to_procure = fields.Float(
        help='Set the product quantity to procure.',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0,
    )

    @api.model
    def _prepare_line(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
        }

    @api.model
    def create(self, vals):
        """Method overrided to save the readonly fields values"""
        sale_line_id = self.env['sale.order.line'].browse(
            vals.get('sale_line_id'))
        if sale_line_id:
            vals.update(self._prepare_line(sale_line_id))
        res = super().create(vals)
        return res

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will
        be created from a stock rule comming from a sale order line.
        """
        self.ensure_one()
        return {
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'sale_line_id': self.sale_line_id.id,
            'date_planned': self.date_planned,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
        }

    @api.multi
    def _action_launch_stock_rule(self):
        """ Launch procurement group run method with required/custom fields
        genrated by a sale order line. procurement group will launch
        '_run_pull', '_run_buy' or '_run_manufacture' depending on the
        sale order line product rule.
        """
        proc_group_obj = self.env['procurement.group']
        location_id = self.env.ref('sale_stock_sample.stock_sample_location')
        errors = []
        for line in self:
            product_qty = line.qty_to_procure
            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = proc_group_obj.create({
                    'name': line.order_id.name,
                    'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the
                # order was cancelled, we need to update certain
                # values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({
                        'partner_id': line.order_id.partner_shipping_id.id,
                    })
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({
                        'move_type': line.order_id.picking_policy,
                    })
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param(
                    'stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(
                    product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom
            # Run procurement
            try:
                proc_group_obj.run(
                    product_id=line.product_id,
                    product_qty=product_qty,
                    product_uom=procurement_uom,
                    location_id=location_id,
                    name=line.name,
                    origin=line.order_id.name,
                    values=values
                )
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductAlternativeWizard(models.TransientModel):
    _name = 'product.alternative.wizard'
    _description = 'Change Products Without Stock For Alternative Products'

    line_ids = fields.One2many(
        comodel_name='product.alternative.wizard.line',
        inverse_name='wiz_id',
        string='Lines',
    )

    @api.model
    def _get_available_alternative_products(self, move):
        def recursive_alternative_product(alternatives, alternative_ids):
            for alternative in alternatives.mapped('alternative_id'):
                if alternative.qty_available_not_res >= initial_demand:
                    alternative_ids.append(alternative.id)
                if alternative.alternative_ids:
                    alternative_ids = recursive_alternative_product(
                        alternative.alternative_ids, alternative_ids)
            return alternative_ids
        alternative_ids = []
        initial_demand = move.product_uom_qty
        return recursive_alternative_product(
            move.product_id.alternative_ids, alternative_ids)

    @api.model
    def _prepare_line(self, move):
        return {
            'wiz_id': self.id,
            'product_id': move.product_id.id,
            'uom_id': move.product_uom.id,
            'alternative_ids': [
                (6, 0, self._get_available_alternative_products(move))
            ],
            'move_id': move.id,
        }

    @api.multi
    def compute_lines(self):
        self.ensure_one()
        production = self.env[self._context.get('active_model')].browse(
            self._context.get('active_id'))
        wiz_line_obj = self.line_ids
        miss = []
        for move in production.move_raw_ids.filtered(
                lambda m: not m.reserved_availability):
            line_vals = self._prepare_line(move)
            if not line_vals['alternative_ids'][0][2]:
                miss.append(move.product_id.display_name)
                continue
            line_vals['alternative_id'] = line_vals['alternative_ids'][0][2][0]
            wiz_line_obj.create(line_vals)
        if miss:
            raise UserError(
                _('Error! There are some products without stock and'
                    ' without alternatives with stock. \n %s') % (
                    ('\n').join(miss)
                ))
        action = self.env.ref(
            'mrp_product_alternative.action_product_alternative_wizard')
        res = action.read()[0]
        res['res_id'] = self.id
        return res

    @api.multi
    def change_products(self):
        self.ensure_one()
        for line in self.line_ids:
            line.move_id.write({
                'product_id': line.alternative_id.id,
            })
            line.move_id._action_assign()
        return True


class ProductAlternativeWizardLine(models.TransientModel):
    _name = 'product.alternative.wizard.line'
    _description = ('Lines to Change Products Without Stock For'
                    ' Alternative Products')

    wiz_id = fields.Many2one(
        comodel_name='product.alternative.wizard',
        string='Wizard',
        required=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        readonly=True,
    )
    alternative_id = fields.Many2one(
        comodel_name='product.product',
        strinig='Alternative Product',
    )
    alternative_ids = fields.Many2many(
        comodel_name='product.product',
        readonly=True,
    )
    stock_available_unreserved = fields.Float(
        string='Quantity Available',
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        related='alternative_id.qty_available_not_res'
    )
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        readonly=True,
    )
    move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Raw Move',
        required=True,
        readonly=True,
    )

# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProductionPlan(models.Model):
    _name = 'mrp.production.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production Plan'

    name = fields.Char(readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    user_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self.env.user)
    request_ids = fields.One2many(
        'mrp.production.request', 'plan_id', string='Requests')
    production_ids = fields.One2many(
        'mrp.production', 'plan_id', string='Productions')
    line_ids = fields.One2many('mrp.production.plan.line', 'plan_id')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('to_approve', 'To Be Approved'),
                   ('approved', 'Approved'),
                   ('done', 'Done'),
                   ('cancel', 'Cancelled')],
        index=True, track_visibility='onchange',
        required=True, copy=False, default='draft')

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
        requests = self.env['mrp.production.request'].search([
            ('plan_id', '=', False)])
        for request in requests:
            self.env['mrp.production.plan.line'].create({
                'plan_id': self.id,
                'request_id': request.id,
            })


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
        string='Required Qty', readonly=True, related='request_id.product_qty')
    qty = fields.Float(string='Done')
    sequence = fields.Integer(default=10)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        readonly=True, default='draft')

    @api.onchange('qty')
    def _onchange_field_name(self):
        if self.qty > self.required_qty:
            raise ValidationError(_())

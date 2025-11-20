from odoo import models, api, tools, _
from odoo.tools.safe_eval import safe_eval, wrap_module
from odoo.tools import config
from odoo.osv import expression
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

# Create a safe wrapper for expression module
safe_expression = wrap_module(expression, ['normalize_domain'])


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    @tools.conditional(
        'xml' not in config['dev_mode'],
        tools.ormcache(
            'self.env.uid',
            'self.env.su',
            'model_name',
            'mode',
            'tuple(self._compute_domain_context_values())'
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        try:
            original_domain = super(IrRule, self)._compute_domain(model_name, mode=mode)

            if self.env.su and original_domain == [(1, '=', 1)]:
                return original_domain

            # Skip processing for models used by this access rights system to avoid recursion
            excluded_models = {
                'user.domain.access',
                'access.rights.management',
                'hide.field',
                'hide.view.nodes',
                'hide.chatter',
                'remove.action',
                'menu.item',
                'action.data',
                'view.data',
                'ir.rule',
                'ir.model',
                'ir.model.fields',
            }
            if model_name in excluded_models:
                return original_domain

            # Use UIDs and IDs directly to avoid triggering field access checks that cause recursion
            user_id = self.env.uid
            
            # Get company_id from context first (safest way)
            company_ids = self.env.context.get('allowed_company_ids')
            if not company_ids:
                # Fallback: get company_id directly from database to avoid any field access
                try:
                    self.env.cr.execute(
                        "SELECT company_id FROM res_users WHERE id = %s",
                        (user_id,)
                    )
                    result = self.env.cr.fetchone()
                    company_ids = [result[0]] if result and result[0] else []
                except Exception:
                    return original_domain
            
            if not company_ids:
                return original_domain

            company_id = company_ids[0]

            # Use sudo() and with_context to bypass access rights during rule computation
            domain_rules = self.env['user.domain.access'].with_context(active_test=True).sudo().search([
                ('access_rights_management_id.user_ids', '=', user_id),
                ('model_name', '=', model_name),
                ('access_rights_management_id.company_ids', 'in', company_ids),
                ('access_rights_management_id.active', '=', True)
            ])

            if not domain_rules:
                return original_domain

            # Create recordsets for eval context without triggering extra queries
            user = self.env['res.users'].browse(user_id)
            company = self.env['res.company'].browse(company_id)
            
            eval_context = {
                'user': user,
                'current_company': company,
                'context': self.env.context,
                'uid': user_id,
                'time': datetime.now(),
            }

            custom_domains = []
            for rule in domain_rules:
                if not rule.assignment_domain:
                    continue

                try:
                    dom = safe_eval(
                        rule.assignment_domain,
                        eval_context,
                        {
                            'expression': safe_expression,
                            '_': _,
                        }
                    )
                    if dom:
                        custom_domains.append(safe_expression.normalize_domain(dom))
                except Exception as e:
                    _logger.error(
                        "Failed to evaluate domain for rule ID %s (User: %s, Model: %s): %s",
                        rule.id, user.id, model_name, str(e)
                    )
                    continue

            if not custom_domains:
                return original_domain

            if original_domain == [(1, '=', 1)]:
                return expression.AND(custom_domains) if len(custom_domains) > 1 else custom_domains[0]
            return expression.AND([original_domain] + custom_domains)
            
        except Exception as e:
            _logger.error("Error in _compute_domain for model %s: %s", model_name, str(e))
            return original_domain
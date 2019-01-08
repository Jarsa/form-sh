# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class MrpEco(models.Model):
    _inherit = "mrp.eco"

    survey_id = fields.Many2one(
        'survey.survey',
        string='Survey',
    )
    has_survey = fields.Boolean(
        compute='_compute_has_survey',
    )

    @api.multi
    @api.depends('survey_id')
    def _compute_has_survey(self):
        for rec in self:
            rec.has_survey = bool(rec.survey_id)

    @api.multi
    def action_answer_survey(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': _("Results of the Survey"),
            'url': self.survey_id.with_context(relative_url=True)
            .public_url + "/phantom"
        }

    @api.multi
    def action_show_result_survey(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': _("Results of the Survey"),
            'url': self.survey_id.with_context(relative_url=True).result_url
        }

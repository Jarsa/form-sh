# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.survey.controllers.main import Survey
from odoo import http


class SurveyEco(Survey):

    @http.route(auth='user')
    def print_survey(self, survey, token=None, **post):
        return super().print_survey(survey, token, **post)

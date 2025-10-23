# -*- coding: utf-8 -*-

from odoo import models, api

class SaleRequest(models.Model):
    _inherit = 'sale.request'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """Override para eliminar completamente las restricciones de acceso"""
        return True

    @api.model
    def check_access_rule(self, operation):
        """Override para eliminar completamente las reglas de acceso"""
        return True

    def check_access_rights(self, operation, raise_exception=True):
        """Override a nivel de registro para eliminar restricciones"""
        return True

    def check_access_rule(self, operation):
        """Override a nivel de registro para eliminar reglas"""
        return True


class SaleRequestLine(models.Model):
    _inherit = 'sale.request.line'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """Override para eliminar completamente las restricciones de acceso"""
        return True

    @api.model
    def check_access_rule(self, operation):
        """Override para eliminar completamente las reglas de acceso"""
        return True

    def check_access_rights(self, operation, raise_exception=True):
        """Override a nivel de registro para eliminar restricciones"""
        return True

    def check_access_rule(self, operation):
        """Override a nivel de registro para eliminar reglas"""
        return True
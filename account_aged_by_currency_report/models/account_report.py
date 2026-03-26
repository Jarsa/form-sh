# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountReport(models.Model):
    _inherit = 'account.report'

    def _query_get(self, options, date_scope, domain=None):
        """Extiende _query_get para soportar dominios extra inyectados via options.

        Permite que módulos custom añadan filtros adicionales al WHERE de los
        reportes contables sin necesidad de copiar el SQL completo del engine.
        Se usa la clave '_extra_domain' en options para no colisionar con claves
        estándar del framework.
        """
        extra = options.get('_extra_domain', [])
        if extra:
            domain = list(domain or []) + extra
        return super()._query_get(options, date_scope, domain=domain)

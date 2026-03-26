# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner.balance.report.handler"

    def _get_custom_display_config(self):
        """Registra el componente OWL personalizado que agrega el filtro
        de moneda al panel de filtros del reporte de antigüedad.
        Se llama super() para preservar la configuración base
        (css_custom_class y el componente AgedPartnerBalanceLineName).
        """
        config = super()._get_custom_display_config()
        config.setdefault('components', {})
        config['components']['AccountReportFilters'] = 'account_reports.AgedByCurrencyReportFilters'
        return config

    def _custom_options_initializer(self, report, options, previous_options=None):
        """En Odoo 17, las opciones del handler se inyectan aquí, no en _get_options."""
        super()._custom_options_initializer(report, options, previous_options=previous_options)

        # Lista de todas las monedas activas para el dropdown del filtro
        options['currencies'] = self.env['res.currency'].search([('active', '=', True)]).read(['id', 'name'])

        # Moneda seleccionada: preservar la del usuario o usar la de la empresa por defecto
        previous_currency = (previous_options or {}).get('selected_currency')
        if previous_currency and previous_currency != 'company_currency':
            # Verificar que la moneda guardada sigue siendo válida
            currency_ids = {c['id'] for c in options['currencies']}
            if isinstance(previous_currency, int) and previous_currency in currency_ids:
                options['selected_currency'] = previous_currency
                options['selected_currency_name'] = self.env['res.currency'].browse(previous_currency).name
                # Inyectar el domain de moneda para que _query_get lo aplique automáticamente
                options['_extra_domain'] = [('currency_id', '=', previous_currency)]
                _logger.debug("Filtro de moneda activo: currency_id=%s", previous_currency)
                return

        options['selected_currency'] = 'company_currency'
        options['selected_currency_name'] = _('Moneda de la compañía')
        # Sin filtro de moneda: asegurarse de que no quede _extra_domain del ciclo anterior
        options.pop('_extra_domain', None)

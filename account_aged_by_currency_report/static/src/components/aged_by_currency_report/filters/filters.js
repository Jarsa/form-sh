/** @odoo-module */

import { AccountReport } from "@account_reports/components/account_report/account_report";
import { AccountReportFilters } from "@account_reports/components/account_report/filters/filters";
import { _t } from "@web/core/l10n/translation";

export class AgedByCurrencyReportFilters extends AccountReportFilters {
    static template = "account_reports.AgedByCurrencyReportFilters";

    /**
     * Nombre de la moneda actualmente seleccionada para mostrar en el botón del filtro.
     */
    get selectedCurrencyName() {
        const selected = this.controller.options.selected_currency;
        if (!selected || selected === "company_currency") {
            return _t("Moneda de la compañía");
        }
        for (const currency of (this.controller.options.currencies || [])) {
            if (currency.id === selected) {
                return currency.name;
            }
        }
        return _t("Moneda de la compañía");
    }

    /**
     * Actualiza el filtro de moneda y recarga el reporte.
     * @param {number|string} currencyId - ID entero de la moneda o 'company_currency'
     */
    async filterCurrency(currencyId) {
        await this.controller.updateOption("selected_currency", currencyId, true);
    }
}

AccountReport.registerCustomComponent(AgedByCurrencyReportFilters);

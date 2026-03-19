/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SelectionField } from "@web/views/fields/selection/selection_field";

/**
 * Patch SelectionField to gracefully handle the case where the current
 * stored value does not exist in the field's selection options.
 *
 * Without this fix, Odoo throws:
 *   TypeError: Cannot read properties of undefined (reading '1')
 *   at get string (SelectionField)
 *
 * This happens when a record has a selection value that is no longer
 * present in the field definition (e.g. after a migration or module change).
 */
patch(SelectionField.prototype, {
    get string() {
        const option = this.options.find((o) => o[0] === this.props.value);
        if (!option) {
            console.warn(
                `[invoice_view_fix] SelectionField: value "${this.props.value}" ` +
                `not found in options for field "${this.props.name}". ` +
                `Returning empty string to prevent crash.`
            );
            return this.props.value !== undefined && this.props.value !== false
                ? String(this.props.value)
                : "";
        }
        return option[1];
    },
});

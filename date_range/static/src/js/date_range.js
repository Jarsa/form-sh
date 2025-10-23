/* Copyright 2016 ACSONE SA/NV (<https://acsone.eu>)
 * Copyright 2021 Studio73 - Pablo Fuentes (https://www.studio73.es)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

// DISABLED FOR ODOO 17 COMPATIBILITY - CAUSES MODULE LOADING ERRORS
// odoo.define("date_range.CustomFilterItem", function (require) {
//     "use strict";

//     // Try the new imports first, fallback to old ones
//     let _t, session, FIELD_OPERATORS, FIELD_TYPES, CustomFilterItem, patch;

//     try {
//         // Odoo 17 style imports
//         _t = require("@web/core/l10n/translation")._t;
//         session = require("@web/session").session;
//         const searchUtils = require("@web/search/utils/misc");
//         FIELD_OPERATORS = searchUtils.FIELD_OPERATORS;
//         FIELD_TYPES = searchUtils.FIELD_TYPES;
//         CustomFilterItem = require("@web/search/custom_filter_item/custom_filter_item").CustomFilterItem;
//         patch = require("@web/core/utils/patch").patch;
//     } catch (e) {
//         // Fallback to old style imports
//         const core = require("web.core");
//         _t = core._t;
//         session = require("web.session");
//         const searchUtils = require("web.searchUtils");
//         FIELD_OPERATORS = searchUtils.FIELD_OPERATORS;
//         FIELD_TYPES = searchUtils.FIELD_TYPES;
//         CustomFilterItem = require("web.CustomFilterItem");

//         // For older versions, create a simple patch function
//         patch = function (obj, name, methods) {
//             Object.assign(obj, methods);
//         };
//     }

//     // Create the enhancement
//     const DateRangeCustomFilterItem = CustomFilterItem.extend({
//         init: function () {
//             this._super.apply(this, arguments);
//             this._computeDateRangeOperators();
//         },

//         _computeDateRangeOperators: function () {
//             const self = this;
//             this.OPERATORS = Object.assign({}, FIELD_OPERATORS);
//             this.OPERATORS.date = [...FIELD_OPERATORS.date];
//             this.OPERATORS.datetime = [...FIELD_OPERATORS.datetime];
//             this.date_ranges = {};

//             return this._rpc({
//                 model: "date.range",
//                 method: "search_read",
//                 fields: ["name", "type_id", "date_start", "date_end"],
//                 context: session.user_context,
//             }).then(function (result) {
//                 result.forEach(function (range) {
//                     const range_type = range.type_id[0];
//                     if (self.date_ranges[range_type] === undefined) {
//                         const r = {
//                             symbol: "between",
//                             description: _t("in") + " " + range.type_id[1],
//                             date_range: true,
//                             date_range_type: range_type,
//                         };
//                         self.OPERATORS.date.push(r);
//                         self.OPERATORS.datetime.push(r);
//                         self.date_ranges[range_type] = [];
//                     }
//                     self.date_ranges[range_type].push(range);
//                 });
//             });
//         },

//         _setDefaultValue: function (condition) {
//             const type = this.fields[condition.field].type;
//             const operator = this.OPERATORS[FIELD_TYPES[type]][condition.operator];
//             if (operator && operator.date_range) {
//                 const default_range = this.date_ranges[operator.date_range_type][0];
//                 // Use moment if available, otherwise fallback to Date
//                 if (window.moment) {
//                     const d_start = moment(default_range.date_start + " 00:00:00");
//                     const d_end = moment(default_range.date_end + " 23:59:59");
//                     condition.value = [d_start, d_end];
//                 } else {
//                     const d_start = new Date(default_range.date_start + "T00:00:00");
//                     const d_end = new Date(default_range.date_end + "T23:59:59");
//                     condition.value = [d_start, d_end];
//                 }
//             } else {
//                 this._super.apply(this, arguments);
//             }
//         },

//         _onValueInput: function (condition, ev) {
//             const type = this.fields[condition.field].type;
//             const operator = this.OPERATORS[FIELD_TYPES[type]][condition.operator];
//             if (operator && operator.date_range) {
//                 const eid = parseInt(ev.target.value);
//                 const ranges = this.date_ranges[operator.date_range_type];
//                 const range = ranges.find(function (x) { return x.id == eid; });
//                 if (range) {
//                     // Use moment if available, otherwise fallback to Date
//                     if (window.moment) {
//                         const d_start = moment(range.date_start + " 00:00:00");
//                         const d_end = moment(range.date_end + " 23:59:59");
//                         condition.value = [d_start, d_end];
//                     } else {
//                         const d_start = new Date(range.date_start + "T00:00:00");
//                         const d_end = new Date(range.date_end + "T23:59:59");
//                         condition.value = [d_start, d_end];
//                     }
//                 }
//             } else {
//                 this._super.apply(this, arguments);
//             }
//         },
//     });

//     // Try to patch the original class if possible
//     if (patch && CustomFilterItem.prototype) {
//         patch(CustomFilterItem.prototype, "date_range.CustomFilterItem", DateRangeCustomFilterItem.prototype);
//     }

//     return DateRangeCustomFilterItem;
// });
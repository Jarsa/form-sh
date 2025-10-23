// odoo.define('google_spreadsheet_import.google_spreadsheet', function (require) {
// "use strict";

// var core = require('web.core');
// var BaseImport = require('base_import.import');


// function jsonp(form, attributes, callback) {
//     attributes = attributes || {};
//     var options = {jsonp: _.uniqueId('import_callback_'), 'from_drive': true};
//     window[options.jsonp] = function () {
//         delete window[options.jsonp];
//         callback.apply(null, arguments);
//     };
//     if ('data' in attributes) {
//         _.extend(attributes.data, options);
//     } else {
//         _.extend(attributes, {data: options});
//     }
//     _.extend(attributes, {
//         dataType: 'script',
//     });
//     debugger;
//     $(form).ajaxSubmit(attributes);
// }

// BaseImport.DataImport.include({
//     events: _.extend({}, BaseImport.DataImport.prototype.events, {
//         'click button.oe_import_google_spreadsheet_sync_button': function (e) {
//             this['loaded_file']();
//         },
//     }),
//     onfile_loaded: function () {
//         this['loaded_file']();
//         var file = this.$('input.oe_import_file')[0].files[0];
//         if (!file) {
//             this.$buttons.filter('.o_import_import, .o_import_validate, .o_import_file_reload').addClass('d-none');

//             this.$('.oe_import_date_format').select2('val', '');
//             this.$('.oe_import_datetime_format').val('');

//             this.$el.removeClass('oe_import_preview oe_import_error');
//             var import_toggle = true;
//             this.$el.find('.oe_import_box').toggle(import_toggle);
//             jsonp(this.$el, {
//                 url: '/base_import/set_file'
//             }, this.proxy('settings_changed'));
//         }
//         else {
//             return this._super()
//         }
//     },
// });
// });

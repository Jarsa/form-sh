odoo.define("l10n_mx_portal.send_mail_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "mx_portal_send_mail",
        {
            test: true,
        },
        [
            {
                content: "Send email",
                trigger: "a[title='Send by e-mail'][aria-disabled='false']:first()",
            },
            {
                content: "Wait Confirmation",
                trigger: "h3.alert.alert-success",
            },
        ]
    );
});

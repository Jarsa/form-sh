odoo.define("l10n_mx_portal.generate_invoice_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "mx_portal_generate_invoice",
        {
            test: true,
        },
        [
            {
                trigger: "a.o_download_btn",
                content: "Generate Invoice",
            },
        ]
    );
});

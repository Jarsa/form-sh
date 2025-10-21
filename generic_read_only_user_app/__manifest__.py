# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Generic Read Only User Access",
    "summary": "Adds option to turn all modules into "
    "readonly for specified user",
    "author": "Jarsa Sistemas",
    "version": "14.0.0.0.0",
    "depends": ["base", "sale_management"],
    "license": "LGPL-3",
    "data": [
        "security/user_read_only_group.xml",
        "security/ir.model.access.csv",
        "views/res_user_read_only.xml",
    ],
    "installable": True,
    "auto_install": False,
    "category": "Extra Tools",
}

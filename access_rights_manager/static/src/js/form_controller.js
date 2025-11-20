/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { FormController } from "@web/views/form/form_controller";
import { session } from "@web/session";
import { jsonrpc } from "@web/core/network/rpc_service";
import { onWillStart } from "@odoo/owl";

// Helper function to check restrictions
async function checkRestrictions(userId, modelName) {
    if (!userId || !modelName) return {};
    try {
        return await jsonrpc('/access_rights/check_restrictions', {
            user_id: userId,
            model_name: modelName
        });
    } catch (error) {
        console.error("Failed to check restrictions:", error);
        return {};
    }
}

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.restrictions = {};

        onWillStart(async () => {
            if (this.props.resModel) {
                this.restrictions = await checkRestrictions(session.uid, this.props.resModel);
            }
        });
    },

    get actionMenuItems() {
        const items = super.actionMenuItems;
        if (items?.action) {
            if (this.restrictions.disable_archive) {
                items.action = items.action.filter(
                    item => !["archive", "unarchive"].includes(item.key)
                );
            }
            if (this.restrictions.disable_export) {
                items.action = items.action.filter(
                    item => item.key !== "export"
                );
            }
        }
        return items;
    }
});

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.restrictions = {};

        onWillStart(async () => {
            if (this.props.resModel) {
                this.restrictions = await checkRestrictions(session.uid, this.props.resModel);
            }
        });
    },

    get actionMenuItems() {
        const items = super.actionMenuItems;
        if (items?.action) {
            if (this.restrictions.disable_archive) {
                items.action = items.action.filter(
                    item => !["archive", "unarchive"].includes(item.key)
                );
            }
            if (this.restrictions.disable_export) {
                items.action = items.action.filter(
                    item => item.key !== "export"
                );
            }
        }
        return items;
    }
});
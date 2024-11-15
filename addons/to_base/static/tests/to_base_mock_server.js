/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { MockServer } from "@web/../tests/helpers/mock_server";

patch(MockServer.prototype, {
    /**
     * @override
     */
    async _performRPC(route, args) {
        if (args.model == 'res.config.settings' && args.method == 'get_viin_brand_modules_icon') {
            return Promise.resolve(['viin_brand/static/img/apps/settings.png']);
        }
        return super._performRPC(...arguments);
    },
});

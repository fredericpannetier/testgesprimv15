odoo.define('always_bottom_chatter.DiFormRenderer', function(require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');
    var config = require('web.config');


    var DiFormRenderer = FormRenderer.include({
        //copie standard
        _applyFormSizeClass: function() {
            const formEl = this.$el[0];
            if (config.device.size_class <= config.device.SIZES.XS) {
                formEl.classList.add('o_xxs_form_view');
            } else {
                formEl.classList.remove('o_xxs_form_view');
            }
            // if (config.device.size_class === config.device.SIZES.XXL) {
            //     formEl.classList.add('o_xxl_form_view');
            // } else {
            //     formEl.classList.remove('o_xxl_form_view');
            // }
        },

    });

    return DiFormRenderer;

});
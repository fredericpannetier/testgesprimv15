odoo.define('widget_last_prices.LastPricesWidget', function (require) {
"use strict";


var core = require('web.core');
var QWeb = core.qweb;

var Widget = require('web.Widget');
var widget_registry = require('web.widget_registry');

var _t = core._t;

var LastPricesWidget = Widget.extend({
    template: 'widget_last_prices.lastPricesWidget',
    events: _.extend({}, Widget.prototype.events, {
        'click .fa-line-chart': '_onClickButton',
    }),

    /**
     * @override
     * @param {Widget|null} parent
     * @param {Object} params
     */
    init: function (parent, params) {
        this.data = params.data;
        this.fields = params.fields;
        this._super(parent);
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._setPopOver();
        });
    },
    
    updateState: function (state) {
        this.$el.popover('dispose');
        var candidate = state.data[this.getParent().currentRow];
        if (candidate) {
            this.data = candidate.data;
            this.renderElement();
            this._setPopOver();
        }
    },

    _getContent() {
        const $content = $(QWeb.render('widget_last_prices.PricesDetailPopOver', {
            data: this.data,
        }));
        
        return $content;
    },
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * Set a bootstrap popover on the current LastPricesWidget widget that display last
     * prices.
     */
    _setPopOver() {
        const $content = this._getContent();
        if (!$content) {
            return;
        }
        const options = {
            content: $content,
            html: true,
            placement: 'left',
            title: _t('Last prices'), // TODO n'apparait pas dans les traductions , à voir
            trigger: 'focus',
            delay: {'show': 0, 'hide': 100 },
        };
        this.$el.popover(options);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    _onClickButton: function () {
        // We add the property special click on the widget link.
        // This hack allows us to trigger the popover (see _setPopOver) without
        // triggering the _onRowClicked that opens the order line form view.
        this.$el.find('.fa-line-chart').prop('special_click', true);
    },
});

widget_registry.add('last_prices_widget', LastPricesWidget);

return LastPricesWidget;
});

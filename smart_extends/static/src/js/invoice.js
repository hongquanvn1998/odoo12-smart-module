odoo.define('invoice', function(require) {
    var AbstractField = require('web.AbstractField')
    var fieldRegistry = require('web.field_registry')

    var invoiceField = AbstractField.extend({
        events: {
            'click .o_invoice_number': 'clickInvoice'
        },
        init: function(parent, field, $node) {
            this.invoice_number = $node.data[field]
            this._super.apply(this, arguments);
        },

        _renderReadonly: function() {
            this._super.apply(this, arguments);
            this.$el.html(() => {
                let _inv = '000000' + this.invoice_number;
                return '<span class="badge badge-success">' + _inv.substr(0, 7) + '</span>'
            })
        },
    })

    fieldRegistry.add('invoice', invoiceField)

    return { invoiceField: invoiceField }
});
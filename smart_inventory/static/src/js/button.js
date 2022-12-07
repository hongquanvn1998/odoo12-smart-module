odoo.define('smart_inventory.change_params', function(require) {
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var qweb = core.qweb;
    // console.log('Da goi vao day')
    
    var BillsListController = ListController.extend({
        // buttons_template: 'change_params',
        /**
         * Extends the renderButtons function of ListView by adding an event listener
         * on the bill upload button.
         *
         * @override
         */
        renderButtons: function() {
            this._super.apply(this, arguments); // Possibly sets this.$buttons
            if (this.$buttons) {
                var self = this;
                this.$buttons.on('click', '.change_params_button', function() {
                    // console.log('Da goi vao day')
                    var state = self.model.get(self.handle, { raw: true });
                    var context = state.getContext()
                    context['type'] = 'in_invoice'
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'inventory.wizard',
                        target: 'new',
                        views: [
                            [false, 'form']
                        ],
                        context: context,
                    });
                });

                this.$buttons.on('click', '.stock_print_button', function() {
                    var state = self.model.get(self.handle, { raw: true });
                    var context = state.getContext()
                    context['type'] = 'print_report'
                    self.do_action({
                        data: {
                            "model": "stock.inventory.wizard",
                            "context": JSON.stringify(context)
                        },
                        type: "ir.actions.report",
                        report_name: "smart_inventory.stock_inventory_report_template",
                        report_type: "qweb-pdf",
                        report_file: "smart_inventory.stock_inventory_report_template",
                        name: "Stock Inventory Report",
                        flags: {}
                    });
                });
            }
        }
    });

    var BillsListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: BillsListController,
        }),
    });

    viewRegistry.add('smart_inventory_change_params', BillsListView);

});
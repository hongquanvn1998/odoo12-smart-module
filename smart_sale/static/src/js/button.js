odoo.define('smart_sale.change_params', function(require) {
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var qweb = core.qweb;
    
    
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
                this.$buttons.on('click', '.sale_change_params_button', function() {
                    var state = self.model.get(self.handle, { raw: true });
                    var context = state.getContext()
                    context['type'] = 'sale_report'
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'sale.wizard',
                        target: 'new',
                        views: [
                            [false, 'form']
                        ],
                        context: context,
                    });
                });

                this.$buttons.on('click', '.sale_print_button', function() {
                    var state = self.model.get(self.handle, { raw: true });
                    var context = state.getContext()
                    context['type'] = 'print_report'
                    self.do_action({
                        data: {
                            "model": "sale.wizard",
                            "context": JSON.stringify(context)
                        },
                        type: "ir.actions.report",
                        report_name: "smart_sale.reportjournal_display",
                        report_type: "qweb-pdf",
                        report_file: "smart_sale.reportjournal_display",
                        name: "Sale Journal Report",
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

    viewRegistry.add('smart_sale_change_params', BillsListView);

});

// var need_import = document.getElementsByClassName('o_view_nocontent')[0].getElementsByTagName('p')[1]
// console.log(need_import)
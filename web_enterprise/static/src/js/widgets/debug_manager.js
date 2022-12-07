odoo.define('web_enterprise.DebugManager', function (require) {
"use strict";

var config = require('web.config');
var WebClient = require('web.WebClient');

// var includeF = {
//     /**
//      * States whether the current environment is in debug or not.
//      *
//      * @param debugMode the debug mode to check, empty for simple debug mode
//      * @returns {boolean}
//      */
//     isDebug: function (debugMode) {
//         if (debugMode) {
//             return odoo.debug && odoo.debug.indexOf(debugMode) !== -1;
//         }
//         return odoo.debug;
//     },
// }

// config.include(includeF)

// if (config.isDebug()) {
    // WebClient.include({
    //     start: function() {
    //         var self = this;
    //         return this._super.apply(this, arguments).then(function () {
    //             // Override toggle_home_menu to trigger an event to update the debug manager's state
    //             var toggle_home_menu = self.toggle_home_menu;
    //             self.toggle_home_menu = function (display) {
    //                 var action, controller;
    //                 if (!display) {
    //                     action = self.action_manager.getCurrentAction();
    //                     controller = self.action_manager.getCurrentController();
    //                 }
    //                 self.current_action_updated(action, controller);
    //                 toggle_home_menu.apply(self, arguments);
    //             };
    //         });
    //     },
    //     instanciate_menu_widgets: function() {
    //         var self = this;
    //         return this._super.apply(this, arguments).then(function() {
    //             // Compatibility with community debug manager
    //             self.systray_menu = self.menu.systray_menu;
    //         });
    //     },
    // });
// }

});

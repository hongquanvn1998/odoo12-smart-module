# -*- coding: utf-8 -*-
from odoo import http

# class SmartInventory(http.Controller):
#     @http.route('/smart_inventory/smart_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_inventory/smart_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_inventory.listing', {
#             'root': '/smart_inventory/smart_inventory',
#             'objects': http.request.env['smart_inventory.smart_inventory'].search([]),
#         })

#     @http.route('/smart_inventory/smart_inventory/objects/<model("smart_inventory.smart_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_inventory.object', {
#             'object': obj
#         })
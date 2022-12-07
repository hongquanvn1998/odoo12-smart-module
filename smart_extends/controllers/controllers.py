# -*- coding: utf-8 -*-
from odoo import http

# class SmartExtends(http.Controller):
#     @http.route('/smart_extends/smart_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_extends/smart_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_extends.listing', {
#             'root': '/smart_extends/smart_extends',
#             'objects': http.request.env['smart_extends.smart_extends'].search([]),
#         })

#     @http.route('/smart_extends/smart_extends/objects/<model("smart_extends.smart_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_extends.object', {
#             'object': obj
#         })
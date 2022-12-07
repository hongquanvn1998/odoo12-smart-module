# -*- coding: utf-8 -*-
from odoo import http

# class SmartUserLocation(http.Controller):
#     @http.route('/smart_user_location/smart_user_location/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_user_location/smart_user_location/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_user_location.listing', {
#             'root': '/smart_user_location/smart_user_location',
#             'objects': http.request.env['smart_user_location.smart_user_location'].search([]),
#         })

#     @http.route('/smart_user_location/smart_user_location/objects/<model("smart_user_location.smart_user_location"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_user_location.object', {
#             'object': obj
#         })
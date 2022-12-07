# -*- coding: utf-8 -*-
from odoo import http

# class SmartDashboard(http.Controller):
#     @http.route('/smart_dashboard/smart_dashboard/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_dashboard/smart_dashboard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_dashboard.listing', {
#             'root': '/smart_dashboard/smart_dashboard',
#             'objects': http.request.env['smart_dashboard.smart_dashboard'].search([]),
#         })

#     @http.route('/smart_dashboard/smart_dashboard/objects/<model("smart_dashboard.smart_dashboard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_dashboard.object', {
#             'object': obj
#         })
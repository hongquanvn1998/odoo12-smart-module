# -*- coding: utf-8 -*-
from odoo import http

# class SmartTranslate(http.Controller):
#     @http.route('/smart_translate/smart_translate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_translate/smart_translate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_translate.listing', {
#             'root': '/smart_translate/smart_translate',
#             'objects': http.request.env['smart_translate.smart_translate'].search([]),
#         })

#     @http.route('/smart_translate/smart_translate/objects/<model("smart_translate.smart_translate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_translate.object', {
#             'object': obj
#         })
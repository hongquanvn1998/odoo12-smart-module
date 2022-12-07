# -*- coding: utf-8 -*-
from odoo import http

# class SmartInvoice(http.Controller):
#     @http.route('/smart_invoice/smart_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_invoice/smart_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_invoice.listing', {
#             'root': '/smart_invoice/smart_invoice',
#             'objects': http.request.env['smart_invoice.smart_invoice'].search([]),
#         })

#     @http.route('/smart_invoice/smart_invoice/objects/<model("smart_invoice.smart_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_invoice.object', {
#             'object': obj
#         })
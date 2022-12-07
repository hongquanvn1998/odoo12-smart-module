# -*- coding: utf-8 -*-
from odoo import http

# class SmarterpSale(http.Controller):
#     @http.route('/smarterp_sale/smarterp_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smarterp_sale/smarterp_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smarterp_sale.listing', {
#             'root': '/smarterp_sale/smarterp_sale',
#             'objects': http.request.env['smarterp_sale.smarterp_sale'].search([]),
#         })

#     @http.route('/smarterp_sale/smarterp_sale/objects/<model("smarterp_sale.smarterp_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smarterp_sale.object', {
#             'object': obj
#         })
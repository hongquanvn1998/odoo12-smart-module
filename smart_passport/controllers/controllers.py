# -*- coding: utf-8 -*- 
from odoo.http import route,  Controller, content_disposition, dispatch_rpc, request


class SmartPassport(Controller):
    @route('/api/signin', type='json' ,website=True,  auth='public')
    def signin(self, **post):
        if post.get('domain') is None or post.get('username') is None or post.get('password') is None:
            return {'err':'error request'}
        uid = request.session.authenticate(post.get('domain'),post.get('username'),post.get('password')) 
        return  {'uid': uid, 'user':request.env['ir.http'].session_info()}

#     @http.route('/smart_passport/smart_passport/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_passport.listing', {
#             'root': '/smart_passport/smart_passport',
#             'objects': http.request.env['smart_passport.smart_passport'].search([]),
#         })

#     @http.route('/smart_passport/smart_passport/objects/<model("smart_passport.smart_passport"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_passport.object', {
#             'object': obj
#         })
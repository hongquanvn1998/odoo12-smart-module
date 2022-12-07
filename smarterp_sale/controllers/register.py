#Author: Thiep Wong
#Created: 17/6 2019
#Register module to buy

from odoo import http
from odoo.http import request
from werkzeug.utils import redirect
import json

class Register(http.Controller):
    @http.route('/register/trial',auth='public')
    def index(self, **kw): 
        #i = 0
        _prod = request.env['product.product'].sudo().search([('active','=','true'),('type','=','service'),('categ_id','=',4)])
        #for _pr in _prod:
            #_pr.mapped('pricelist_item_ids')
            ##_pricelist = request.env['product.pricelist.item'].search([('product_tmpl_id','=',_pr.product_tmpl_id.id)])
            #_pr.name = 'Deo biet duoc'
            #if _pricelist:
               # _pr.price_extra = _pricelist.fixed_price 
        try:
            _user = request.env['product.product'].sudo().search([('active','=','true'),('type','=','service'),('default_code','=','user_count')])

        except:
            return "error"


        _state = request.env['res.country.state'].sudo().search([('country_id','=',1)])
        response = http.request.render('smarterp_sale.register_page',{'products':_prod,'user':_user, 'states':_state})
        response.headers['X-Frame-Options'] = 'DENY'
       
        return response
 
    @http.route('/register/new-customer', auth='public', type='json')
    def addnew(self,**kw):  
        partner = request.env['res.partner'].sudo().create({
            'name':kw['fullname'],
            'vat':kw['taxcode'],
            'street':kw['address'],
            'city':kw['district'],
            'state_id':kw['state'],
            'email':kw['email'],
            'phone':kw['phone'],
            'mobile':kw['mobile'],
            'is_company':kw['iscompany']
        })
        request.env.cr.commit()


        if kw["iscompany"] == 1:
            request.env["res.company"].sudo().create({
                'name':kw['fullname'],
                'company_register':kw['fullname'],
                'email':kw['email'],
                'phone':kw['phone'] ,
                'partner_id':partner.id,
                'company_registry':kw['fullname']
            }) 
            request.env.cr.commit() 
  
        return partner.read()

    @http.route('/register/products', auth='public', type='json')
    def products(self,**kw):
        m = request.env['product.product'].sudo().search([('active','=','true'),('type','=','service'),('categ_id','=',4)]) 
        return m.read()

    @http.route('/register/user-service', auth='public', type='json')
    def userservice(self,**kw):
        m = request.env['product.product'].sudo().search([('active','=','true'),('type','=','service'),('default_code','=',kw['default_code'])])
        return m.read()


    @http.route('/register/order',auth='public',type='json')
    def order(self, **kw):
        order = request.env['sale.order'].sudo().create({
            'partner_id': 10, 
            'pricelist_id': 1,
            'picking_policy': 'direct', 
            'create_uid':2,
            'write_uid':2,
            'order_line': [(0, 0, {'name': 'CRM',
                                   'product_id': 2,
                                   'product_uom_qty': 1,
                                   'product_uom': 1})]})

        m = order.action_confirm()
        return m

    @http.route('/register/insert',auth='public',type='json')
    def insert(self, **kw):
        order = request.env['smarterp_sale.register'].sudo().create({
            'partner_id': 10, 
            'email': 'thiep.wong@gmail.com',
            'domain':'xinchao'
        })

        #m = order.action_confirm()
        request.env.cr.commit()
        return order.read()

    @http.route('/register/validate', auth='public', type='json')
    def validate(self, **kw):
        #Check the register db
        register_id = request.env['smarterp_sale.register'].search([('email','=',kw['email'])])
        if register_id.id > 0:
            return False 
        return True
    

    @http.route('/register/districts',auth='public', type='json')
    def district_list(self, **kw):
        districts = request.env['res.district'].sudo().search([('state_id','=',kw['state_id'])],order="name asc")
        return districts.read()
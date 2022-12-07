from odoo import http
from odoo.http import request
import json
import werkzeug
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date
import datetime
from odoo.http import Response
import requests
import base64
import io
from odoo.service import db
from odoo.addons.smart_init.controllers  import http as ht


class SmartManager(http.Controller):

    @http.route('/api/check-exist-database',csrf=False,type='http',auth='public',method=['POST'])
    def check_exist_database(self,**kw):
        if(db.exp_db_exist(kw['shopDomain'])==True): 
            data = {
                'success':False,
                'message':'Tên miền %s.smarterp.vn đã tồn tại, vui lòng thay đổi tên miền của shop!' % kw['shopDomain'],
            }
        else:
            data = {
                'success':True,
                'message':'Thành công',
            }
        return json.dumps(data)
        

    @http.route('/api/app-modules',csrf=False,type='http',auth='public',method=['POST'])
    def app_modules(self,**kw):
        price_list = {}
        if 'id_period' in kw:
            app_price = request.env['smart_manager.app_price'].search([('period','=',int(kw['id_period']))])
            for i in app_price:
                price_list['%s'%i.app.id] = {
                    'id':i.id,
                    'name':i.name,
                    'appName':i.app.name,
                    'dependApps':[ a.id for a in i.app.depend_apps],
                    'basePrice':i.price,
                    'appId':i.app.id,
                    'image':'/web/image?model=product.template&id=%d&field=image' %i.app.id,
                    'checked':False,
                }
        else:
            pass
        return  json.dumps(price_list) 

    @http.route('/register/form',type='http',auth='public',method=['POST'],website=True,csrf=False)
    def register_submit(self, **kw): 
        _prod = request.env['product.product'].sudo().search([])
        try:
            _user = request.env['product.product'].sudo().search([('active','=','true'),('type','=','service'),('default_code','=','user_count')])

        except:
            return "error"


        _state = request.env['res.country.state'].sudo().search([('country_id','=',1)])
        response = http.request.render('smart_manager.register_form',{'products':_prod,'user':_user, 'states':_state})
        response.headers['X-Frame-Options'] = 'DENY'
       
        return response
 
    @http.route('/api/business-category',csrf=False,auth='public',type='http',method=['POST'])
    def business_category(self,**kw): 
        business_category = request.env['smart_manager.business_category'].sudo().search([])
        return json.dumps([{
            "id": i.id,
            "name": i.name,
            "code": i.code,
            "icon":    i.icon.decode('ASCII'), 
        } for i in business_category ])


    @http.route('/api/payment-period',csrf=False,auth='public',type='http',method=['POST'])
    def payment_period(self,**kw): 
        payment_periods = request.env['smart_manager.payment_period'].sudo().search([])
        return json.dumps({
            'monthly': [{
            "id": i.id,
            "name": i.name,
            "isAnnualy": i.is_annualy,
            "value":   i.value, 
        } for i in payment_periods if i.is_annualy ==False  ],
        'annualy':[{
            "id": i.id,
            "name": i.name,
            "isAnnualy": i.is_annualy,
            "value":   i.value, 
        } for i in payment_periods if i.is_annualy ==True ]})
    
    @http.route('/api/area-register',csrf=False,type="http",auth="public",method=['POST'])
    def pos_area(self,**kw):
        response_province = http.request.env['province'].search([])
        list_province=[]
        list_district=[]
        list_ward = []
        if len(kw)<1:
            for res in response_province:
                val = {
                    'id': res.id,
                    'name': res.name,
                    'code_province':res.code_province,
                    'is_province':True,
                }
                list_province.append(val)
        elif 'province_id' in kw:
            for t in http.request.env['district'].search([('parent_code','=',kw['province_id'])]):
                val_t = {
                    'id': t.id,
                    'name': t.name,
                    'parent_code':t.parent_code,
                    'code_district':t.code_district,
                    'is_district':True,
                }
                list_district.append(val_t)
        else:
            for w in http.request.env['ward'].search([('parent_code','=',kw['district_id'])]):
                val_w = {
                    'id': w.id,
                    'name': w.name,
                    'parent_code':w.parent_code,
                    'is_ward':True,
                }
                list_ward.append(val_w)
        data = {
            'province':list_province,
            'district':list_district,
            'ward':list_ward,
        }
        return json.dumps(data)
    
    @http.route('/api/submit-register-form',csrf=False,auth='public',type='json',method=['POST'])
    def submit_form(self,**kw):
        data = {
            'partner_name':kw['form']['partnerName'],
            'mobile':kw['form']['mobile'],
            'email':kw['form']['email'],
            'use_type':kw['form']['useType'],
            'shop_domain':kw['form']['shopDomain'],
            'username':kw['form']['username'],
            'password':kw['form']['password'],
            'verify_type':'mobile',
            'name':kw['form']['partnerName'],
            'business_size':kw['form']['businessSize'],
            'business_category':kw['form']['businessCategoryId'],
            'register_type':("annualy" if kw['form']['isAnnualy'] else "monthly"),
            'register_quantity':kw['form']['paymentPeriods'],
            'install_apps':[(6,0,kw['form']['appPrice'])],
            'state':'registered',
            'province':kw['form']['province'],
            'district':kw['form']['district'],
            'ward':kw['form']['ward'],
        }
        try:
            response = request.env['smart_manager.register'].sudo().create(data)
            data = {
                'message': 'Đăng ký thành thành công!',
                'code': 200,
                'status': True,
                'result':response
            }
            return json.dumps(data)
        except Exception as ex:
            data = {
                'message': 'Đăng ký thất bại: %s!' %(ex.args[0]),
                'code': 400,
                'status': False,
            }
            return json.dumps(data)




# -*- coding: utf-8 -*-

from six import print_
from odoo import models, fields, api, _
from odoo.models import check_method_name
from odoo.http import request
from odoo.service import db
import uuid
import base64
import json
import requests
import threading
# import grpc
import os
import redis

from odoo.exceptions import UserError 
from odoo.api import call_kw, Environment 

from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import sleep
# from odoo.addons.smart_init.models import base_pb2
# from odoo.addons.smart_init.models import base_pb2_grpc
from odoo.addons.smart_init.models import apps
# import sys
# sys.path.insert(0, './smart_init/models')
# import base_pb2,base_pb2_grpc
# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
# from Crypto import Random

import logging
_logger = logging.getLogger(__name__)
_logger.debug("This is my debug message ! ")


class Register (models.Model):
    _name = 'smart_manager.register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = _('Register Request')

    BUSINESS_TYPE_SELECTION =  [('person', 'Personal'), ('company', 'Company')]
    BUSINESS_SIZE_SELECTION = [( 0, '<10'), (1, '10-30'), (2, '31-50'), (3, '51-100'), (4, '100-200'), (5, '>200')]
    STATE_SELECTION = [( 'draft',_('Draft')),( 'registered',_('Registered')), ('verifying', _('Verifying')), ('verified', _('Verified')),
    ('initialing',_('Initialing')), ('activated', _('Activated')), ('expired', _('Expired')), ('cancelled', _('Cancelled'))]
    VERIFY_TYPE_SELECTION = [('mobile','Mobile'),('email','Email')]

    REGISTER_TYPE_SELECTION = [('monthly', _('Monthly')),('annualy',_('Annualy'))]
    REGISTER_QUANTITY_SELECTION = [(1,'1 month'),(3,'3 months'),(6,'6 months'),(9 ,'9 months')]
    USING_TYPE_SELECTION = [('trial', _('Trial')), ('business',_('On Business'))]

    #Business infomations  
    use_type =    fields.Selection(
        string='Using Type',
        selection=USING_TYPE_SELECTION
    )

    business_type =  fields.Selection(
        string='Business Type',
        selection=BUSINESS_TYPE_SELECTION
    )

    business_size =   fields.Selection(
        string='Business Size',
        selection=BUSINESS_SIZE_SELECTION
    ) 
    
    business_category =   fields.Many2one(
        string='Business Model',
        comodel_name='smart_manager.business_category',
        ondelete='restrict',
    )

    verify_type = fields.Selection(
        string='Verify Type',
        selection=VERIFY_TYPE_SELECTION,
        default="mobile"
    )

    state =   fields.Selection(
        string='Status',
        selection= STATE_SELECTION,
        default="draft"
    )
    note = fields.Text(string='Note')
     

    #Account infomation
    name = fields.Char(string='Shop Name')
    code = fields.Char(string='Register Code')
    business_tax_code = fields.Char(string='Tax Code')
    business_tax_address = fields.Char(string='Company tax address', none= True, blank=True) 
    shop_domain = fields.Char(string='Shop domain')
    partner = fields.Many2one(string='Partner', comodel_name='res.partner')
    employee =  fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        ondelete='restrict',
    )

    order =    fields.One2many(
        string='Order',
        comodel_name='sale.order',
        inverse_name='order_register',
    )
   
    partner_name = fields.Char(string='Customer Name')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')

    register_date =   fields.Datetime(
        string='Register Date',
        default=fields.Datetime.now,
    )
    activated_date =  fields.Datetime(
        string='Activated Date',
    ) 
    expired_date = fields.Datetime(
        string='Expired Date',
    ) 

    register_type =   fields.Selection(
        string='Register Type',
        selection=REGISTER_TYPE_SELECTION,
        blank=False, none=False,
        required = True,
        default='monthly'
    )

    register_quantity = fields.Many2one(
        string='Register Quantity',
        comodel_name='smart_manager.payment_period',
        ondelete='restrict',
           required = True
    ) 
    province =  fields.Many2one(
        string='Province',
        comodel_name='province',
        ondelete='restrict',
    )
    district =  fields.Many2one(
        string='District',
        comodel_name='district',
        ondelete='restrict',
    )
    ward =  fields.Many2one(
        string='Ward',
        comodel_name='ward',
        ondelete='restrict',
    )

    username = fields.Char(string='Username')
    password = fields.Char(string='Password')

    install_apps =   fields.Many2many(
        string='Install Apps',
        comodel_name='smart_manager.app_price',
        relation='smart_manager_register_app_price_rel',
        column1='register_id',
        column2='price_id',
        domain="[('enable', '=', True )]"
    ) 
 
    @api.onchange('register_type')
    def _onchange_register_type(self):
        _annualy_type =True if self.register_type == 'annualy' else False
        self.register_quantity = False
        self.install_apps = False
        return {'domain': {'register_quantity': [('is_annualy', '=',_annualy_type)]}}

    @api.onchange('register_quantity')
    def _onchange_register_quantity(self) :
        return {'domain': {'install_apps':[('period','=', self.register_quantity.id)]}}
    
    

    @api.onchange('province')
    def onchange_province(self):
        res = {}
        self.district = False
        parent_code = ''
        if self.province:
            list_district = self.env['district'].search([('parent_code', '=', self.province.code_province)])
            if len(list_district) > 0:
                parent_code = list_district[1].parent_code
            res = {'domain': {'district': [('parent_code', '=', parent_code)]}}
        else:
            res = {}
        return res    
 
    @api.onchange('district')
    def onchange_district(self):
        res = {}
        self.ward = False
        parent_code = ''
        if self.district:
            list_ward = self.env['ward'].search([('parent_code', '=', self.district.code_district)])
            if len(list_ward) > 0:
                parent_code = list_ward[0].parent_code
            res = {'domain': {'ward': [('parent_code', '=', parent_code)]}}
        return res

   
    @api.model
    def create(self, vals):  
            vals['password'] = self.encrypt(vals['password'])
            res = super().create(vals)  
            _code =  uuid.uuid4().hex
            res.code = _code.upper()
            return res

    @api.onchange('install_apps')
    def onchange_install_apps(self):
        list_app = self.install_apps.ids
        for e in self.install_apps:
            if e.app.depend_apps:
                for v in e.app.depend_apps:
                    app = self.env['smart_manager.app_price'].search([('period','=', self.register_quantity.id),('app','=',v.id)])
                    if app: 
                        list_app.append(app.id)
        self.update({'install_apps': [(6,0,list_app)] })
    

    # Action method  
    def action_register_register(self):
        if(db.exp_db_exist(self.shop_domain)==True): 
            raise UserError(_('Tên miền %s.smarterp.vn đã tồn tại, vui lòng thay đổi tên miền của shop!' % self.shop_domain))
        else:
            self.state = 'registered'
            msg = _('The request form %s has been registered!' % self.code)
            self.message_post(body=msg)

    def action_register_verify(self):
        old_list_app = self.install_apps.ids
        new_list_app = []
        for e in self.install_apps:
            if e.app.depend_apps:
                for v in e.app.depend_apps:
                    app = self.env['smart_manager.app_price'].search([('period','=', self.register_quantity.id),('app','=',v.id)])
                    if app: 
                        new_list_app.append(app.id)
        if all(v in old_list_app for v in new_list_app):
            self.state = 'verifying' 
            msg = _('The request form %s is verifying now!' % self.code)
            self.message_post(body=msg)
        else:
            error = 'Không đủ app kèm theo'
            return UserError(_(error)) 

    def action_register_confirm(self):  
        vals = {
                'name': self.partner_name,
                'vat': self.business_tax_code or None,
                'mobile': self.mobile or None, 
                'company_type': self.business_type or None,
                'email': self.email or None,
                'province':self.province.id or '',
                'district':self.district.id or '',
                'ward':self.ward.id or '',
            }
        self.partner = self.env['res.partner'].sudo().create(vals) 
        self.state = 'verified'
        msg = _('The request form %s has been verified!' % self.code)
        self.message_post(body=msg)
  
    def action_register_re_verify(self):
        self.state = 'verifying'


    def action_register_cancel(self): 
        self.state = 'cancelled'
        msg = _('The request form %s has been cancelled!' % self.code)
        self.message_post(body=msg)

    def action_register_to_draft(self):
        self.state = 'draft' 
        msg = _('The request form %s has been drafted!' % self.code)
        self.message_post(body=msg)
        
    def _call_kw(self, model, method, args, kwargs):
        check_method_name(method)
        return call_kw(request.env[model], method, args, kwargs)

    def action_register_create_database(self): 
        with api.Environment.manage():  
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr)) 
            try:
                
                list_apps = [i.app.default_code for i in self.install_apps]
                list_apps[:0] = ['mail']
                _logger.info('Lay duoc list app ==============> %s'%list_apps)

                # split url
                new_url = ''
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                list_url = base_url.split('://')
                split_url = list_url[1].split('.')
                domain = split_url[1]
                _logger.info(' ====================================================>xong domain')

                if 2 < len(split_url):
                    new_url = '%s://%s.%s.%s'%(list_url[0],self.shop_domain,domain,split_url[2])
                else:
                    new_url = '%s://%s.%s'%(list_url[0],self.shop_domain,domain)
                _logger.info('====================================================> This is new domain %s'%new_url)
                
                # new_cr.commit()
                # new_cr.close() 

                user_admin_config = self.env['ir.config_parameter'].sudo().get_param('smart_manager.user_admin'),
                if user_admin_config[0]:
                    _super_users = user_admin_config[0]
                    _passw_super_users = '%s123..' % user_admin_config[0].split('@')[0]
                else:
                    _super_users = 'admin@smarterp.vn'
                    _passw_super_users = 'admin123..'

                _logger.info('Start create database') 

                apps._exp_create_database(self.shop_domain, False, 'vi_VN', _passw_super_users, _super_users, 'vn', self.partner.mobile)
                url_channel = domain.split(':')[0]

                login_url = "%s/web/session/authenticate"%new_url
                _logger.info('Login URL --------------------------------------------------->: %s'% login_url)
                headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache"}
                params = {
                    "params":{
                        "db": self.shop_domain,
                        "login": _super_users,
                        "password": _passw_super_users,
                        "context": {}
                    }
                }
                response = requests.post(login_url, json=params, headers=headers, verify=False)
                _logger.info('Login successful')

                cookie = response.headers['set-cookie']
                headers["Cookie"] = cookie

                json_data = {
                    "params": {
                        "args": [
                            list_apps, {
                                "lang": "vi_VN",
                                "tz": "Asia/Ho_Chi_Minh",
                                "uid": 2,
                                "search_default_app": 1
                            }
                        ],
                        "user":{
                            "login": _super_users,
                            "password": _passw_super_users,
                        },
                        "partner":{"name":self.partner_name,
                        "login":self.username,
                        "password": self.decrypt(self.password).decode("ascii") ,
                        "email":self.email},
                        "expired_date":(str(datetime.now() + relativedelta(months=self.register_quantity.value)) if(self.register_type == 'monthly') else str(datetime.now() + relativedelta(years=self.register_quantity.value)) ),
                        "method": "button_immediate_install",
                        "model": "ir.module.module"
                    },
                } 

                install_url = "%s/web/dataset/app_install" %new_url
                sleep(5)
                requests.post(install_url, json=json_data, headers=headers) 

                return 
            except Exception as e:
                _logger.error('Error client')
                _logger.error(str(e))
                self.state = 'verified'
                self._cr.commit()
                self._cr.rollback()
                self._cr.close()
                error = "Database creation error: %s" % self.shop_domain 
                return UserError(_(error))
                raise UserError(_(error))
    
    def action_register_init_db(self):
        _logger.info('Qua dau tien')
        try:
            self.write({ 'state':'initialing' })
            _logger.info('====================================================> Qua tao self env')

            # create sale order
            if self.install_apps:
                _logger.info('====================================================> Create sale order')

                _order = self.env['sale.order'].sudo().create({
                    'partner_id': self.partner.id,
                    'state':'draft',
                    'order_line': [(0, 0, {
                        'name': (product.app.name if product.app.default_code == False else '[%s] %s'%(product.app.default_code,product.app.name) ), 
                        'product_id': product.app.id, 
                        'product_uom_qty': 1, 
                        'product_uom': product.app.uom_id.id, 
                        'price_unit': product.price}) for product in self.install_apps],
                    'app_sale':True,
                    'order_register':self.id,
                })
                _logger.info('====================================================> create_invoice_config')
                create_invoice_config = bool(self.env['ir.config_parameter'].sudo().get_param('smart_manager.create_invoice')),
                if self.use_type == 'business' and create_invoice_config :
                    _logger.info('====================================================> create invoice')

                    Invoice = self.env['account.invoice']
                    _order.order_line.read(['name', 'price_unit', 'product_uom_qty', 'price_total'])
                    # send quotation
                    _logger.info('====================================================> SEND QUOTATION')

                    _order.force_quotation_send()
                    _order.order_line._compute_product_updatable()

                    # confirm quotation
                    _logger.info('====================================================> Confirm QUOTATION ')

                    _order.action_confirm()

                    # create invoice: only 'invoice on order' products are invoiced
                    _logger.info('====================================================> PRODUCT ARE INVOICED')

                    inv_id = _order.action_invoice_create()
                    invoice = Invoice.browse(inv_id)
                    _order.order_line._compute_product_updatable()
                _logger.info('====================================================> Order = order')
                
                order = _order
                self.ensure_one()
                _logger.info('====================================================> Add order id')

                # try:
                _logger.info('====================================================> (4,order.id)')
                update_order = [(6, 0, [order.id])]
                self.write({ 'order':update_order })
                # except Exception as e:
                #     _logger.info('====================================================> self.order = order.id')

                # self.order = order.id
            _logger.info('====================================================> self.state = activated')
            
            self.state = 'activated'
            # self.activated_date = fields.Datetime.to_datetime(datetime.now())
            self.activated_date = str(datetime.today())
            # self.expired_date = fields.Datetime.to_datetime(self.activated_date + relativedelta(months=self.register_quantity.value)) if(self.register_type == 'monthly') else fields.Datetime.to_datetime(self.activated_date + relativedelta(years=self.register_quantity.value))
            self.expired_date = str(datetime.today())
            _logger.info('====================================================> commit')
        except Exception as e:
            self.state = 'verified'

        _logger.info('Update state')

        threaded_calculation = threading.Thread(target=self.action_register_create_database ) 
        threaded_calculation.setDaemon(True)
        threaded_calculation.start() 
        return True 

    def encrypt(self, char):
        _pwd = base64.b64encode(str.encode(char)).hex()
        return _pwd


    def decrypt(self,key):
        _char = base64.b64decode(bytes.fromhex(key))
        return _char

    def get_traffic(self):
        # r = redis.StrictRedis(host="localhost",port=6379,password="")
        # split url
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        list_url = base_url.split('://')
        url = list_url[0]+"://"+self.shop_domain+"*"
        # for key in r.keys(url):
        #     data = r.hgetall(key.decode("utf8"))
        #     hello = data[b'count'].decode("utf8")
        #     print(data)

        return self.env['report.traffic'].reload_data({'url':url})

        

    
    
    

    
    
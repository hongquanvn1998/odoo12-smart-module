# -*- coding: utf-8 -*-

import time
# import grpc
import threading
import odoo
import logging
import base64

from datetime import datetime
from concurrent import futures
from odoo.service import db

# from . import base_pb2
# from . import base_pb2_grpc

from odoo import models, fields, api, _,SUPERUSER_ID
from odoo.http import request
from odoo.addons.web.controllers.main import clean_action
from odoo.api import call_kw, Environment as Ev
from odoo.models import check_method_name
from odoo.exceptions import UserError



_logger = logging.getLogger(__name__)

grpc_servers = {}
# class InstallAppServicer(base_pb2_grpc.InstallAppServicer):
#     def __init__(self,cr):
#         self.env = Ev(cr,SUPERUSER_ID,{})
    
#     def decrypt(self,key):
#         _char = base64.b64decode(bytes.fromhex(key))
#         return _char

#     def InstallApplication(self,request,context):
#         partner = {
#             "name":request.name,
#             "login":request.login,
#             "password": self.decrypt(request.password).decode("ascii") ,
#             "email":request.email
#         }
#         args = [
#             request.app_modules, {
#                 "lang": "vi_VN",
#                 "tz": "Asia/Ho_Chi_Minh",
#                 "uid": 2,
#                 "search_default_app": 1
#             }
#         ],
#         self.env['smart_init.apps'].app_install(partner,request.model,request.expired_date,request.method,args)
#         response = base_pb2.AppResponse()
#         response.success = True
#         return response


class smart_init(models.Model):
    _name = 'smart_init.apps'

    name = fields.Char(string='Name')
    login = fields.Char(string='User')
    email = fields.Char(string='Email')
    password = fields.Char(string='Password')
    pos = fields.Boolean(string='Completed',default=False)

    # @api.model
    # def start_server(self):
    #     with api.Environment.manage():
    #         new_cr = self.pool.cursor()
    #         self = self.with_env(self.env(cr=new_cr))
    #         server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #         base_pb2_grpc.add_InstallAppServicer_to_server(InstallAppServicer(self.env.cr),server)
    #         server.add_insecure_port('[::]:10010')
    #         server.start()
    #         _logger.info('***************************Starting server. Listening on port 10010*************************************')


    def _call_kw(self, model, method, args, kwargs):
        check_method_name(method)
        return call_kw(self.env[model], method, args, kwargs)

    def app_install(self,partner, model, expired_date,method, args, domain_id=None, context_id=None):
        _logger.info('QUa day roi dooooooooooooooooooooo')

        threaded_calculation = threading.Thread(target=self.install_app_module,args=(partner,model, expired_date, method, args))
        threaded_calculation.setDaemon(True)
        threaded_calculation.start()
        return True

    @api.model
    def install_app_module(self,partner,model, expired_date,method,args,domain_id=None, context_id=None):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            try:
                modules = args[0]

                _mod_ids = self.env[model].search([('name','in',modules)]).ids   
                args[0]=_mod_ids
                if 'smart_pos' in modules:
                    partner['pos'] = True
                action = self._call_kw(model, method, args, {})
                self.env['smart_init.apps'].sudo().create(partner)
                self.env['ir.config_parameter'].sudo().set_param('database.expiration_date',datetime.strptime(expired_date.split('.')[0],'%Y-%m-%d %H:%M:%S'))
                if isinstance(action, dict) and action.get('type') != '':
                    clean_action(action)
                new_cr.commit()
                new_cr.close()
                return {}

            except Exception as e:
                self._cr.rollback()
                self._cr.close()
                error = "Database creation error"
                print(error)
                print(str(e))
                return UserError(_(error)) 

@db.check_db_management_enabled
def _exp_create_database(db_name, demo, lang, user_password='admin', login='admin', country_code=None, phone=None):
    """ Similar to exp_create but blocking."""
    _logger.info('Create database `%s`.', db_name)
    db._create_empty_database(db_name)
    db._initialize_db(id, db_name, demo, lang, user_password, login, country_code, phone)
    return True
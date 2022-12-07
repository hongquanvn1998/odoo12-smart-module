# -*- coding: utf-8 -*-
from odoo import http,api,_
from odoo.http import request
from odoo.addons.web.controllers.main import clean_action
from odoo.api import call_kw, Environment
from odoo.models import check_method_name
from odoo.exceptions import UserError
from odoo import registry as registry_get

import threading
import logging

from odoo.addons.smart_init.controllers  import http as ht

_logger = logging.getLogger(__name__)


class SmartInit(http.Controller):

    def check_user(self, uid=None):
        if uid is None:
            uid = request.uid
        is_admin = request.env['res.users'].browse(uid)._is_admin()
        if not is_admin:
            raise AccessError(_("Only administrators can upload a module"))

    @http.route('/web/dataset/app_install', type='json', auth="public", method=['POST'])
    def app_install(self,user,partner, model,expired_date, method, args, domain_id=None, context_id=None):
        _logger.info('QUa day roi dayyyyyyyyyyyyyyyyyyyyyyyyyyy')
        uid = request.session.authenticate(request.db, user['login'], user['password'])
        self.check_user(uid)
        # threaded_calculation = threading.Thread(target=self.install_app_module,args=(dbname,model, method, args))
        threaded_calculation = threading.Thread(target=request.env['smart_init.apps'].app_install,args=(partner,model,expired_date, method, args))
        threaded_calculation.start()
        return True
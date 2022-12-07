# -*- coding: utf-8 -*-
from odoo import http

class SmartInventoryReport(http.Controller):
    @http.route('/report/stock-inventory/', auth='user', type="json")
    def index(self, **kw):
        return "Hello, world"
# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import xlwt
import xlsxwriter
import unicodedata
import base64
import io
from io import StringIO
import csv
import babel.numbers
import decimal
class ReportRevenue(models.TransientModel) :
    _name = 'pos.revenue.wizard'

        
    start_date = fields.Date(required=True, default=fields.Date.today)
    end_date = fields.Date(required=True, default=fields.Date.today)
    # @api.multi
    def set_params_to_list(self):  
        params = {
                'start_date' :self.start_date,
                'end_date' :self.end_date,
        } 
        return self.env.get('report.pos.revenue').reload_data(params)
       

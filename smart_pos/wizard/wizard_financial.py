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
class ReportFinancial(models.TransientModel) :
    _name= 'financial.wizard'
    filter_time=fields.Selection(
        string=u'',
        selection=[
            (0, 'by month'), 
            (1, 'by quarter'),
            (2, 'by year'),
        ],default='0',
    )
    # @api.multi
    def set_params_to_list(self):  
        params = {
                'filter_time' :self.filter_time,
        } 
        return self.env.get('').reload_data(params)

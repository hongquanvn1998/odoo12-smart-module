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

class ReportRewardPointHistory(models.TransientModel) :
    _name = 'pos.reward.point.history.wizard'
        
    start_date = fields.Date(required=True, default=fields.Date.today)
    end_date = fields.Date(required=True, default=fields.Date.today)
    
    def _get_default_partner(self):
        return self.env['res.partner'].search([('customer', '=', 'True')]).ids        
    filter_partner = fields.Many2one(string='Customer',comodel_name ='res.partner',domain=['&',('active','=',True),('customer', '=', True)])

    # @api.multi
    def set_params_to_list(self):  
        params = {
                'start_date' :self.start_date,
                'end_date' :self.end_date,
                'filter_partner': self.filter_partner,
        }
        return self.env.get('report.reward.point.history').reload_data(params) 
              

    

      
       

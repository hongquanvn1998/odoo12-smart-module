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
    _name = 'pos.seller.wizard'

        
    start_date = fields.Date(required=True, default=fields.Date.today)
    end_date = fields.Date(required=True, default=fields.Date.today)

    
    def _get_default_employee(self):
        return self.env['res.users'].search([('active','=','True')]).ids
        
    filter_employee = fields.Many2one(string='Employee',comodel_name ='res.users',domain=[('active','=',True)])


    # @api.multi
    def set_params_to_list(self):  
        params = {
                'start_date' :self.start_date,
                'end_date' :self.end_date,
                'filter_employee': self.filter_employee,
        } 
        return self.env.get('report.sale.by.employee').reload_data(params)



      
       

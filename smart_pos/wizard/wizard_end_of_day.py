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
class ReportEndOfDay(models.TransientModel) :
    _name= 'end.of.day.wizard'
    filter_types= fields.Selection(
        string=u'',
        selection=[
            (0, 'Order'), 
            (1, 'Receipts/Expenses'),
            (2, 'Goods'),
            ],default=0,
    )
    def _get_default_partner(self):
        return self.env['res.partner'].search([('customer', '=', 'True')]).ids
        
    def _get_default_employee(self):
            return self.env['res.users'].search([('active','=','True')]).ids


    start_date = fields.Date(required=True, default=fields.Date.today)
    filter_partner = fields.Many2one(string='Customer',comodel_name ='res.partner',domain=['&',('active','=',True),('customer', '=', True)])
    # filter_partner = fields.Many2one(string='Employee',comodel_name ='res.partner',domain=['&',('active','=',True),('customer', '=', True)])

    filter_employee = fields.Many2one(string='Employee',comodel_name ='res.users',domain=[('active','=',True)])
    filter_method_payment= fields.Selection(
        string=u'Selection',
        selection=[
            (0, 'money'), 
            (1, 'card'),
            (2, 'transfer money'),
            ],default=0,
    )
    # @api.multi
    def set_params_to_list(self):  
        params = {
            'start_date' :self.start_date,
                'filter_types': self.filter_types,
                'filter_partner': self.filter_partner,
                'filter_employee': self.filter_employee,
                'filter_method_payment': self.filter_method_payment,
        } 
        if self.filter_types==0:
            return self.env.get('report.end.of.day.by.sale').reload_data(params)
        if self.filter_types==1:
            return self.env.get('report.end.of.day.by.receipts.expenses').reload_data(params)
        if self.filter_types==2:
            return self.env.get('report.end.of.day.by.goods').reload_data(params)

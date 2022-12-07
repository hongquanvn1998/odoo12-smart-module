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
class ReportSale(models.TransientModel) :
    _name = 'pos.sale.wizard'
    
  
    start_date = fields.Date(required=True, default=fields.Date.today)
    end_date = fields.Date(required=True, default=fields.Date.today)
    # filter_pricelist = fields.Many2one(string='Goods', comodel_name='product.pricelist')
    filter_types_sale = fields.Selection(
        string=u'Types',
        selection=[
            (0, 'Order'), 
            (1, 'Profit'),
            (2, 'Employee'),
            ],default=0,
    )


    
    @api.multi
    def set_params_to_list(self):  
        params = {
                'start_date' :self.start_date,
                'end_date' :self.end_date,
        }
        #         'filter_pricelist': self.filter_pricelist,
        # } 
        if self.filter_types_sale==0:
            return self.env.get('report.sale.by.time').reload_data(params)
        if self.filter_types_sale==1:
            return self.env.get('report.sale.by.profit').reload_data(params)
        if self.filter_types_sale==2:
            return self.env.get('report.sale.by.employee').reload_data(params)

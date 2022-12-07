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
class ReportGoods(models.TransientModel) :
    _name = 'goods.wizard'

    filter_types_goods= fields.Selection(
        string=u'',
        selection=[
            (0, 'sale'), 
            (1, 'profit'),
            ],default=0,
    )
    def _get_default_product(self):
        products=self.env['product.product'].search([('active','=',True),('sale_ok','=',True)]).ids
        return products
    def _get_default_product_cate(self):
        cate=self.env['product.category'].search([]).ids
        return cate
        
    start_date = fields.Date(required=True, default=fields.Date.today)
    end_date = fields.Date(required=True, default=fields.Date.today)
    filter_goods=fields.Many2one(string='Goods',comodel_name ='product.product' ,domain=['&',('active','=',True),('sale_ok','=',True)])
    filter_goods_category= fields.Many2one(string='Goods',comodel_name ='product.category')
    # @api.multi
    def set_params_to_list(self):  
        params = {
                'start_date' :self.start_date,
                'end_date' :self.end_date,
                'filter_goods': self.filter_goods,
                'filter_goods_category': self.filter_goods_category,
        } 
        if self.filter_types_goods==0:
             return self.env.get('report.goods.by.sale').reload_data(params)
        if self.filter_types_goods==1:
             return self.env.get('report.goods.by.profit').reload_data(params)

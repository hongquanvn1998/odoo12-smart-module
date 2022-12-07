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
class FilterPurchaseJournalDetail(models.TransientModel) :
    _name= 'filter.purchase.journal.detail'
    

    date_start = fields.Date(required=True, default=str(datetime.today().replace(day=1)))
    date_end = fields.Date(required=True, default=fields.Date.today)
    filter_date= fields.Selection(
        string=u'',
        selection=[
            ('0', 'From the beginning of month to the present'), 
            ('1', 'This quarter'),
            ('2', 'From the early quarter to the present'),
            ('3', 'This year'),
            ('4', 'From the beginning of the year to present'),
            ('5', 'The first half of the year'),
            ('6', 'The last half of the year '),
            ],
            default='0'
    )
    filter_product_categories = fields.Many2one(
        string=u'',
        comodel_name='product.category',
        required=True
    )
    @api.multi
    def get_default_all_product(self):
      return  self.env['product.template'].search([]).ids

    filter_product = fields.Many2many(
        'product.template',
         default = get_default_all_product
    )

    @api.onchange('filter_product_categories')
    def _get_product_by_category(self):
        product_template = self.env['product.template']
        categ_ids= (self.to_number(self.filter_product_categories))
        if categ_ids ==1 :
             products = product_template.search([])
        else :
             products = product_template.search([('categ_id', '=',categ_ids)])
        self.filter_product= products

    @api.onchange('filter_date')
    def get_date(self):
       if self.filter_date is False : pass
       else:
           t= self.getmonth(self)
           if int(self.filter_date) ==0 :
                self.date_start = str(datetime.today().replace(day=1))
                self.date_end = str(datetime.today())
           if int(self.filter_date) ==1 :
                self.date_start = t['date_start']
                self.date_end= t['date_end']
           if int(self.filter_date) ==2 :
                self.date_start = t['date_start']
                self.date_end = str(datetime.today())
           if int(self.filter_date) ==3 :
                  self.date_start = str(datetime.today().replace(day=1,month=1))
                  self.date_end = str(datetime.today().replace(day=31,month=12))
           if int(self.filter_date) ==4 :
                  self.date_start = str(datetime.today().replace(day=1,month=1))
                  self.date_end = str(datetime.today())
           if int(self.filter_date) ==5 :
                self.date_start = str(datetime.today().replace(day=1,month=1))
                self.date_end = str(datetime.today().replace(day=30,month=6))
           if int(self.filter_date) ==6 :
                self.date_start = str(datetime.today().replace(day=1,month=7))
                self.date_end = str(datetime.today().replace(day=31,month=12))
    @staticmethod
    def getmonth(self):
      currentMonth = datetime.now().month
      if 1 <currentMonth <=3 :
         self.date_start = str(datetime.today().replace(day=1,month=1))
         self.date_end = str(datetime.today().replace(day=31,month=3))
      if 3< currentMonth <=6 :
         self.date_start = str(datetime.today().replace(day=1,month=4))
         self.date_end = str(datetime.today().replace(day=30,month=6))
      if 6< currentMonth <=9:
         self.date_start = str(datetime.today().replace(day=1,month=7))
         self.date_end = str(datetime.today().replace(day=30,month=9))
      else:
         self.date_start = str(datetime.today().replace(day=1,month=10))
         self.date_end = str(datetime.today().replace(day=31,month=12))
      return  {'date_start': self.date_start, 'date_end': self.date_end}

    @staticmethod
    def to_number(str):
        number =0
        for value in str:
                try:
                    number =(int(value))
                except ValueError:
                    continue
        return number

    @api.multi
    def get_report (self):
        data ={
            'ids': self.ids,
            'model': self._name,
            'form': {
                 'filter_date' :self.filter_date,
                 'date_start': self.date_start,
                 'date_end': self.date_end,
                 'filter_product' : self.filter_product
            },
        }
        return self.env.ref('smart_purchase.purchase_journal_detail_report').report_action(self, data=data)

class PurchaseJournalDetailGetView(models.AbstractModel):
    _name = 'report.smart_purchase.purchase_journal_detail_report_display'
    

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        date_end= date_end + ' 23:59:59'
        filter_date= data['form']['filter_date']
        filter_product= data['form']['filter_product']
        product_ids= (tuple(self.to_array(filter_product)))
        if len(product_ids) == 0 :
            docs = []
            return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
        }
            pass
        else :
           self.env.cr.execute(
               """
            select 
            distinct
            sp.date_done as accounting_date,
            po.date_approve as voucher_date,
            po.name as voucher_number,
            ai.date_invoice as bill_date,
            ai.number as bill_number,
            pp.default_code as default_code,
            pl.name as product_name,
            uu.name as uom_name,
            pl.qty_received as product_uom_qty,
            pl.price_unit as price_unit,
            pl.price_subtotal as price_subtotal,
            pl.price_tax as price_tax
            from purchase_order_line pl
            left join  purchase_order po
            on po.id= pl.order_id
            left join stock_move sm 
            on sm.purchase_line_id= pl.id
            left join stock_picking sp
            on sm.picking_id = sp.id
            left join account_invoice ai
            on po.id= ai.purchase_id
            left join stock_move_line sml
            on sml.picking_id= sp.id
            left join product_product pp
            on pl.product_id = pp.product_tmpl_id
            left join uom_uom uu
            on pl.product_uom= uu.id
            where pl.product_id in %s
            and  sml.date >= %s and sml.date <= %s and sp.state='done'
            order by po.name
               """

            ,(product_ids,date_start, date_end)
           )
        self.purchase_order = self.env.cr.fetchall() 
        docs = []
        sum_product_uom_qty =0
        sum_price_subtotal= 0
        sum_amount_returned= 0
        sum_return_value= 0
        for item in self.purchase_order:
            if item[8] is None  :
                sum_product_uom_qty += sum_product_uom_qty
            else:
                sum_product_uom_qty += item[8]    
            if item[10] is None  : 
                sum_price_subtotal += sum_price_subtotal 
            else:
               sum_price_subtotal += item[10]  
            docs.append({
                     'accounting_date' : item[0],
                     'voucher_date':  item[1],
                     'voucher_number':item[2],
                     'bill_date': item[3],
                     'bill_number':item[4],
                     'default_code': item[5],
                     'product_name': item[6],
                     'uom_name': item[7],
                     'product_uom_qty':  item[8],
                     'price_unit': item[9],
                     'price_subtotal':  item[10],
                     'price_tax':  item[11],
                     'amount_returned': '',
                     'return_value': '',
                     'value_discount':'' 
                })
                
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'sum_product_uom_qty' :sum_product_uom_qty ,
            'sum_price_subtotal' :sum_price_subtotal ,
            'sum_amount_returned' :sum_amount_returned ,
            'sum_return_value' : sum_return_value,
        }


        
    @staticmethod
    def to_array(str):
       list = []
       for value in str:
               try:
                   list.append(int(value))
               except ValueError:
                   continue
       return list

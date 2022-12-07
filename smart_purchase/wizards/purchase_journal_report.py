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
class ReportPurchaseJournalWizard(models.TransientModel):
   _name= 'purchase.journal.wizard'
   start_date = fields.Date(required=True, default=str(datetime.today().replace(day=1)))
   end_date = fields.Date(required=True, default=fields.Date.today)
   filter_status = fields.Boolean('State')
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
    
   @api.onchange('filter_date')
   def get_date(self):
         if self.filter_date is False : pass
         else:
           t= self.getmonth(self)
           if int(self.filter_date) ==0 :
                self.start_date = str(datetime.today().replace(day=1))
                self.end_date = str(datetime.today())
           if int(self.filter_date) ==1 :
                self.start_date = t['start_date']
                self.end_date= t['end_date']
           if int(self.filter_date) ==2 :
                self.start_date = t['start_date']
                self.end_date = str(datetime.today())
           if int(self.filter_date) ==3 :
                  self.start_date = str(datetime.today().replace(day=1,month=1))
                  self.end_date = str(datetime.today().replace(day=31,month=12))
           if int(self.filter_date) ==4 :
                  self.start_date = str(datetime.today().replace(day=1,month=1))
                  self.end_date = str(datetime.today())
           if int(self.filter_date) ==5 :
                self.start_date = str(datetime.today().replace(day=1,month=1))
                self.end_date = str(datetime.today().replace(day=30,month=6))
           if int(self.filter_date) ==6 :
                self.start_date = str(datetime.today().replace(day=1,month=7))
                self.end_date = str(datetime.today().replace(day=31,month=12))
   @staticmethod
   def getmonth(self):
         currentMonth = datetime.now().month
         if 1 <currentMonth <=3 :
            self.start_date = str(datetime.today().replace(day=1,month=1))
            self.end_date = str(datetime.today().replace(day=31,month=3))
         if 3< currentMonth <=6 :
            self.start_date = str(datetime.today().replace(day=1,month=4))
            self.end_date = str(datetime.today().replace(day=30,month=6))
         if 6< currentMonth <=9:
            self.start_date = str(datetime.today().replace(day=1,month=7))
            self.end_date = str(datetime.today().replace(day=30,month=9))
         if 9 < currentMonth <= 12 :
            self.start_date = str(datetime.today().replace(day=1,month=10))
            self.end_date = str(datetime.today().replace(day=31,month=12))
         return  {'start_date': self.start_date, 'end_date': self.end_date}
 
   def set_params_to_list(self):  
         params = {
                  'start_date':self.start_date,
                  'end_date': self.end_date, 
            } 
         
         return self.env.get('report.purchase.journal').reload_data(params)


class PurchaseJournalGetView(models.AbstractModel):
   _name = 'report.smart_purchase.purchase_journal_report_display'
   @api.model
   def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= end_date + ' 23:59:59'
        filter_status= data['form']['filter_status']
        filter_date= data['form']['filter_date']
        state='purchase'
        if filter_status is False :
            self.env.cr.execute(
               """
            select 
            distinct
            sp.date_done as accounting_date,
            po.date_approve as voucher_date,
            po.name as voucher_number,
            ai.date_invoice as bill_date,
            ai.number as bill_number,
            po.invoice_status as invoice_status,
            po.amount_untaxed as amount_untaxed,
            po.amount_tax as  amount_tax,
            po.amount_total as amount_total,
            po.state as state,
            po.invoice_count as invoice_count
            from purchase_order po 
            left join  purchase_order_line pl
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
            where sml.date >= %s and sml.date <= %s 
            and po.state= %s and sp.state='done'
               """
            ,(start_date, end_date,state)
           )
        else:
          self.env.cr.execute(
               """
            select 
            distinct
            sp.date_done as accounting_date,
            po.date_approve as voucher_date,
            po.name as voucher_number,
            ai.date_invoice as bill_date,
            ai.number as bill_number,
            po.invoice_status as invoice_status,
            po.amount_untaxed as amount_untaxed,
            po.amount_tax as  amount_tax,
            po.amount_total as amount_total,
            po.state as state,
            po.invoice_count as invoice_count
            from purchase_order po 
            left join  purchase_order_line pl
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
            where   sml.date >= %s and sml.date <= %s 
               """
            ,(start_date, end_date)
           )
        self.purchase_order = self.env.cr.fetchall() 
        docs = []
        sum_amount_untaxed= 0
        sum_amount_tax= 0
        sum_amount_total= 0
        for item in self.purchase_order:
            if item[6] is None  :
                sum_amount_untaxed += sum_amount_untaxed
            else:
                sum_amount_untaxed += item[6]    
            if item[7] is None  : 
                sum_amount_tax += sum_amount_tax 
            else:
               sum_amount_tax += item[7]  

            if item[8] is None  : 
               sum_amount_total += sum_amount_total
            else :
               sum_amount_total +=  item[8]
            docs.append({
                   'accounting_date' : item[0],
                   'voucher_date' : item[1],
                   'voucher_number' : item[2],
                   'bill_date' : item[3],
                   'bill_number' :item[4],
                   'invoice_status': item[5],
                   'amount_untaxed' : item[6],
                   'amount_tax' : item[7],
                   'amount_total' : item[8],
                   'state' : item[9],
                   'invoice_count' : item[10]
                })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'start_date': start_date,
            'end_date': end_date,
            'docs': docs,
            'sum_amount_untaxed' :sum_amount_untaxed,
            'sum_amount_tax' : sum_amount_tax,
            'sum_amount_total' : sum_amount_total,
        }
        
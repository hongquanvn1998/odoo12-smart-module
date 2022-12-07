# -*- coding: utf-8 -*-

from odoo import api,models,fields
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, date_utils
import xlwt
import xlsxwriter
import unicodedata
import base64
import io
from io import StringIO
import csv
import babel.numbers
import decimal
from collections import Counter
from odoo.exceptions import ValidationError
from datetime import datetime

from odoo.exceptions import ValidationError

from datetime import date, datetime
import pytz
import json
import io
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportCashLedger(models.TransientModel):
    _name = 'account.balance.sheet'
    # _auto = False

    start_date = fields.Date(required=True,default=str(datetime.today().replace(day=1)))
    end_date = fields.Date(required=True, default=fields.Date.today)
    acc_balance_data = fields.Char('Name', size=256)
    file_name = fields.Binary('File excel', readonly=True)
    filter_date=fields.Selection(
        string=u'',
        selection=[
            ('0', 'From the beginning of month to the present'), 
            ('1', 'This quarter'),
            ('2', 'From the early quarter to the present'),
            ('3', 'This year'),
            ('4', 'From the beginning of the year to present'),
            ('5', 'The first half of the year'),
            ('6', 'The last half of the year '),
        ],default='0',
    )

    account_level=fields.Selection( 
        selection=[
            ("1", "1"), 
            ("2", "2"),
            ("3", "3"), 
        ],default="3",
    )

    balance_with_credit_debit = fields.Boolean(string='Balance with debit/credit', default=True)


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
 
    def get_info(self):
        data ={
            'ids':self.ids,
            'model':self._name,
            'form':{
                'company': self.env.user.company_id.id,  
                'balance_2_side':self.balance_with_credit_debit,
                'account_level':self.account_level,
                'start_date': self.start_date,
                'end_date': self.end_date,
            }
        }
        return self.env.ref('smart_invoice.balance_sheet').report_action(self, data=data)
    def export_excel(self):
        path='../home/export/'           
        
        self.env.cr.execute(
                """
                select  (case when opening.code is not null then opening.code when opening.code is null then incurred.code end ) code , 
                (case when opening.name is not null then opening.name when opening.name is null then incurred.name end ) account_name , 
                COALESCE (opening.debit, 0) opening_debit,  
                COALESCE (opening.credit,0) opening_credit,
                COALESCE (incurred.debit,0) incurred_debit,
                COALESCE (incurred.credit,0) incurred_credit,

                (select max(debit) from unnest(array[0, COALESCE (opening.debit,0)+COALESCE (incurred.debit,0)- COALESCE (incurred.credit,0) - COALESCE (opening.credit,0)]) debit  )  close_debit,
                (select max(credit) from unnest(array[0,COALESCE (opening.credit,0)+COALESCE (incurred.credit,0)- COALESCE (incurred.debit,0) - COALESCE (opening.debit,0)]) credit  )  close_credit  

                from

                (select  
                aa.code,aa.name, sum(aml.debit) debit, sum(aml.credit) credit
                from  
                account_move_line aml   
                left join account_account aa on aa.id = aml.account_id 
                where  
                aml.company_id = %s
                and
                aml.DATE <  %s
                group by aa.code, aa.name 
                order by aa.code ) opening

                full join

                (
                select 

                aa.code,aa.name, sum(aml.debit) debit, sum(aml.credit) credit
                from 

                account_move_line aml   
                left join account_account aa on aa.id = aml.account_id

                where 


                aml.company_id = %s
                and aml.Date >= %s and aml.Date <= %s
                group by aa.code,aa.name 
                order by aa.code ) incurred 
                on opening.code = incurred.code 
                       """ ,(self.env.user.company_id.id,self.start_date,self.env.user.company_id.id,self.start_date,self.end_date)
                    )
        acc_balance = self.env.cr.fetchall() 
        workbook = xlwt.Workbook()                      
        style0 = xlwt.easyxf('font: name Times New Roman , bold on,height 260;align: horiz center;', num_format_str='#,##0.00')
        style1 = xlwt.easyxf('font: name Times New Roman bold on; pattern: pattern solid, fore_colour black;align: horiz center;', num_format_str='#,##0.00')
        style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour black;', num_format_str='#,##0.00')         
        style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
        style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
        style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
        style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
        style7 = xlwt.easyxf('font: name Times New Roman , bold on,height 260;align: horiz center;', num_format_str='#,##0.00')
        style8 = xlwt.easyxf('font: name Times New Roman,bold on,height 480;align: horiz center;', num_format_str='#,##0.00')
        style9 = xlwt.easyxf('font: name Times New Roman,height 260;align: horiz center;',num_format_str='#,##0.00')
        style10 = xlwt.easyxf('font: name Times New Roman,height 260;align: horiz center;')
        
        sheet = workbook.add_sheet(self._name)
        c=7
        sheet.write_merge(2, 4, 4, 20, 'BẢNG CÂN ĐỐI TÀI KHOẢN', style8)
        sheet.write_merge(5, 6, 4, 20, 'Từ ngày : %s Đến ngày: %s' %(self.start_date, self.end_date,), style10) 
        sheet.write_merge(c, c+1,0,0, 'STT', style0)                           
        sheet.write_merge(c, c+1,1,3, 'Số tài khoản', style0)                           
        sheet.write_merge(c, c+1, 4,6,'Tên tài khoản', style0)
        sheet.write_merge(c, c, 7, 12, 'Đầu kỳ', style0)
        sheet.write_merge(c+1, c+1,7,9, 'Nợ', style7)
        sheet.write_merge(c+1, c+1, 10, 12, 'Có', style7)
        sheet.write_merge(c, c, 13, 18, 'Phát sinh', style0)
        sheet.write_merge(c+1, c+1,13,15, 'Nợ', style7)
        sheet.write_merge(c+1, c+1, 16, 18, 'Có', style7)
        sheet.write_merge(c, c, 19, 24, 'Cuối kỳ', style0)
        sheet.write_merge(c+1, c+1,19,21, 'Nợ', style7)
        sheet.write_merge(c+1, c+1,22,24 ,'Có', style7) 
        r = 9; i = 1
        for item in acc_balance:
            sheet.write_merge(r, r,0,0, i)                           
            sheet.write_merge(r, r,1,3, item[0], style9)                           
            sheet.write_merge(r, r, 4, 6, item[1], style9)
            sheet.write_merge(r, r,7,9, item[2], style9)
            sheet.write_merge(r, r, 10, 12, item[3], style9)
            sheet.write_merge(r, r,13,15, item[4], style9)
            sheet.write_merge(r, r, 16, 18, item[5], style9)
            sheet.write_merge(r, r,19,21, item[6], style9)
            sheet.write_merge(r, r,22,24 ,item[7], style9)
            r += 1; i += 1
        filename = ('%s'+ '.xls') %(self._name)
        workbook.save(r'%s%s' %(path,filename))
        fp = open(r'%s%s' %(path,filename), "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)                                                 
                       
# Files actions         
        attach_vals = {
                'acc_balance_data': self._name + '.xls',
                'file_name': out,
            }
            
        act_id = self.env['account.balance.sheet'].create(attach_vals)
        fp.close()
        return {
        'type': 'ir.actions.act_window',
        'res_model': self._name,
        'res_id': act_id.id,
        'view_type': 'form',
        'view_mode': 'form',
        'context': self.env.context,
        'target': 'new',
        }
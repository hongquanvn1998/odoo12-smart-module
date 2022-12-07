from odoo import api,fields,models,_
from datetime import datetime
import time
import pytz
import json
import io
import xlwt
import xlwt
import xlsxwriter
import unicodedata
import base64
import io
from io import StringIO
import csv
import babel.numbers
import decimal
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
class ReportAccountDetail(models.TransientModel):
    _name = 'cash.ledger'

    start_date = fields.Date(required=True,default=str(datetime.today().replace(day=1)))
    end_date = fields.Date(required=True,default=fields.Date.today)
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
    cash_ledger_data = fields.Char('Name', size=256)
    file_name = fields.Binary('File excel', readonly=True)

    @api.multi
    def get_default(self):
        return  self.env['account.account'].search([('code','=','1111')]).ids

    filter_account = fields.Many2many(
        'account.account',
        default= get_default
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

    #@api.multi
    def get_info(self): 
        list=[] 
        for acc in self.filter_account: 
            list.append(acc.code) 
        company_id = self.env.user.company_ids.id
        data ={
            'ids':self.ids,
            'model':self._name,
            'form':{
                'filter_date' :self.filter_date,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'filter_account':list,
                'company_id':company_id,
            }
        }
        return self.env.ref('smart_invoice.cash_ledger').report_action(self,data=data)
    def export_excel(self):
        list = []
        path='../home/export/'          
        for acc in self.filter_account: 
            list.append(acc.code)
        self.env.cr.execute(
                    """
            select 
			incurred.voucher_date,
			incurred.accounting_date,
			incurred.aml_name as  vourcher_name, 
		(case 
		 when opening.code is not null then opening.code else incurred.code
		 end) code,
		 		incurred.counter_part_code, 
		  (CASE 
             WHEN opening.debit is not null
             THEN opening.debit
             ELSE 0
             END)
             AS opening_debit,

               (CASE 
             WHEN incurred.debit is not null
             THEN incurred.debit
             ELSE 0
             END)
             AS  opening_credit,
			  (CASE 
             WHEN incurred.debit is not null
             THEN incurred.debit
             ELSE 0
             END)
             AS incurred_debit,

               (CASE 
             WHEN incurred.credit is not null
             THEN incurred.credit
             ELSE 0
             END)
             AS  incurred_credit,
			incurred .rp_name
			
		from ( select 
            aa.code,
          (CASE 
				WHEN SUM(aml.credit) is not null
				THEN SUM(aml.credit)
				ELSE 0
				END) AS credit,
			 (CASE 
				WHEN SUM(aml.debit) is not null
				THEN SUM(aml.debit)
				ELSE 0
			END) AS debit
            from account_move_line aml
            left join  account_move am
            on aml.move_id = am.id
            left join account_account aa
            on aa.id= aml.account_id
            left join account_journal aj
            on aml.journal_id = aj.id
           where  aml.date <  %s and  aa.code  in %s
           and aml.company_id =%s
            group by aa.code)   opening 
			
			full join
			
			( select 
        aml.date as accounting_date,
        aml.date_maturity as voucher_date,
        aml.name vourcher_name, 
        aa.code,
        ( select array_agg(ab.code) from account_move_line a left join account_account ab on ab.id = a.account_id 
        where a.move_id = aml.move_id and a.account_id !=aml.account_id  group by ab.code limit 1) counter_part_code,
        aml.credit,
        aml.name as aml_name,
        aml.debit,
        aa.name, 
        rp.name as rp_name
        from account_move_line aml

        left join account_move am on am.id = aml.move_id 
        left join account_account aa on aa.id = aml.account_id
        left join account_move_line amls on amls.move_id = aml.move_id
        left join res_partner rp
        on aml.partner_id = rp.id
        where
        aa.code in %s
        and
        aml.date >=  %s and aml.date <= %s
        and aml.company_id =%s

        group by aa.code,aa.name, aml.debit, aml.credit,aml.name,aml.date,counter_part_code,voucher_date,rp.name

        order by aa.code, aml.date
        ) incurred
        on incurred.code = opening.code
             """
                    ,(self.start_date,tuple(list),self.env.user.company_ids.id,tuple(list),self.start_date,self.end_date,self.env.user.company_ids.id)
                )
        self.account_cash = self.env.cr.fetchall() 
        docs = []
        code= ''
        _item=[]
        ob=0
        record = []
        group = []
        _index =0 
        for item in  self.account_cash:
            _index += 1
            if item[3] != code:
                if len(group)>0:
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
                group = []
                group.append(item)
                code = item[3]
                ob=item[5]-item[6]
                if _index >= len(self.account_cash):
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
            else:
                group.append(item)
                if _index >= len(self.account_cash):
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
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
        style11 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz center;', num_format_str='#,##0.00')
        style12 = xlwt.easyxf('font: name Times New Roman,height 260;align: horiz center;',num_format_str='dd-mm-yyyy')
        style13 = xlwt.easyxf('font: name Times New Roman,height 260;align: horiz left;')
        style14 = xlwt.easyxf('font: name Times New Roman ,bold on,height 260;align: horiz left;')
        style15 = xlwt.easyxf('font: name Times New Roman ,bold on,height 260;align: horiz right;')

        

        sheet = workbook.add_sheet(self._name)
        c=7
        sheet.write_merge(2, 4, 4, 22, 'SỔ KẾ TOÁN CHI TIẾT QUỸ TIỀN MẶT', style8)
        sheet.write_merge(5, 6, 4, 22, 'Từ ngày : %s Đến ngày: %s' %(self.start_date, self.end_date,), style10) 
        sheet.write_merge(c, c+1,0,0, 'STT', style0)                           
        sheet.write_merge(c, c+1,1,2, 'Ngày hạch toán', style0)                           
        sheet.write_merge(c, c+1, 3, 4, 'Ngày chứng từ', style0)
        sheet.write_merge(c, c+1, 5, 7, 'Số phiếu thu', style0)
        sheet.write_merge(c, c+1, 8,10,'Số phiếu chi', style0)
        sheet.write_merge(c, c+1, 11,12,'Mô tả', style0)
        sheet.write_merge(c, c+1, 13,14,'Tài khoản', style0)
        sheet.write_merge(c, c+1, 15, 16, 'TK đối ứng', style0)
        sheet.write_merge(c, c, 17, 20, 'Phát sinh', style0)
        sheet.write_merge(c+1, c+1,17,18, 'Nợ', style7)
        sheet.write_merge(c+1, c+1,19,20 ,'Có', style7) 
        sheet.write_merge(c, c+1, 21,23,'Số tồn', style0)
        sheet.write_merge(c, c+1, 24,26,'Người nhận/Người nộp', style0)
        r = 10; i = 1
        tt_inventory = 0;
        tt_debit = 0;
        tt_credit = 0;
        for doc in docs:
            t_ob = doc['ob']
            tt_inventory = tt_inventory + doc['ob']
            sheet.write_merge(r-1, r-1, 1, 7, '', style0)
            sheet.write_merge(r-1, r-1, 8, 12, 'Số tồn đầu kỳ', style15)
            sheet.write_merge(r-1, r-1, 13, 14,doc['code'] , style0 )
            sheet.write_merge(r-1, r-1, 15, 16)
            sheet.write_merge(r-1, r-1,17,18,'0',style0)                           
            sheet.write_merge(r-1, r-1,19,20,'0', style0)                           
            sheet.write_merge(r-1, r-1, 21, 23, doc['ob'], style0)
            sheet.write_merge(r-1, r-1, 24, 26)
            for item in doc['items']:
                t_ob = t_ob + item[7] - item[8]
                tt_debit = tt_debit + item[7]
                tt_credit = tt_credit + item[8]
                tt_inventory= tt_inventory + item[7]-item[8]
                sheet.write_merge(r, r,0,0, i)                           
                sheet.write_merge(r, r,1,2,item[0],style12)                           
                sheet.write_merge(r, r, 3, 4, item[1],style12)
                if item[7]>0:
                    sheet.write_merge(r, r, 5, 7, item[2], style13)
                if item[7] <=0:
                    sheet.write_merge(r, r, 5, 7,'', style13)
                if item[8] >0 :
                    sheet.write_merge(r, r, 8, 10, item[2], style13)
                if item[8] <= 0:
                    sheet.write_merge(r, r, 8, 10, '', style13)
                sheet.write_merge(r, r,11,12, '', style9)
                sheet.write_merge(r, r, 13, 14, item[3], style9)
                sheet.write_merge(r, r, 15, 16, item[4], style9)
                sheet.write_merge(r, r,17,18 ,item[7], style9)
                sheet.write_merge(r, r,19,20 ,item[8], style9)
                sheet.write_merge(r, r,21,23 ,t_ob, style9)
                sheet.write_merge(r, r,24,26 ,item[9], style9)
                r += 1; i += 1
            r += 1; 
        sheet.write_merge(r,r,15,16 ,'Tổng', style0)
        sheet.write_merge(r,r,17,18 ,tt_debit, style11)
        sheet.write_merge(r, r, 19, 20, tt_credit, style11)
        sheet.write_merge(r, r,21,23 ,tt_inventory, style11)
        
        filename = ('%s'+ '.xls') %(self._name)
        workbook.save(r'%s%s' %(path,filename))
        fp = open(r'%s%s' %(path,filename), "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)                                                 
                        
    # Files actions         
        attach_vals = {
                'cash_ledger_data': self._name + '.xls',
                'file_name': out,
            }
            
        act_id = self.env['cash.ledger'].create(attach_vals)
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

class AccountDetailView(models.AbstractModel):
    _name = 'report.smart_invoice.cash_ledger_display'

    @api.model
    def _get_report_values(self,docids,data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= end_date + ' 23:59:59'
        filter_account = data['form']['filter_account']
        company_id= data['form']['company_id']
        account_ids = tuple(filter_account)
        print(account_ids)
        if len(account_ids) == 0 :
                docs = []
                return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_start': start_date,
                'date_end': end_date,
                'docs': docs,
            }
                pass
        else :

        #   str
            self.env.cr.execute(
            """
	    select 
			incurred.voucher_date,
			incurred.accounting_date,
			incurred.aml_name as  vourcher_name, 
		(case 
		 when opening.code is not null then opening.code else incurred.code
		 end) code,
		 		incurred.counter_part_code, 
		  (CASE 
             WHEN opening.debit is not null
             THEN opening.debit
             ELSE 0
             END)
             AS opening_debit,

               (CASE 
             WHEN incurred.debit is not null
             THEN incurred.debit
             ELSE 0
             END)
             AS  opening_credit,
			  (CASE 
             WHEN incurred.debit is not null
             THEN incurred.debit
             ELSE 0
             END)
             AS incurred_debit,

               (CASE 
             WHEN incurred.credit is not null
             THEN incurred.credit
             ELSE 0
             END)
             AS  incurred_credit,
			incurred .rp_name
			
		from ( select 
            aa.code,
          (CASE 
				WHEN SUM(aml.credit) is not null
				THEN SUM(aml.credit)
				ELSE 0
				END) AS credit,
			 (CASE 
				WHEN SUM(aml.debit) is not null
				THEN SUM(aml.debit)
				ELSE 0
			END) AS debit
            from account_move_line aml
            left join  account_move am
            on aml.move_id = am.id
            left join account_account aa
            on aa.id= aml.account_id
            left join account_journal aj
            on aml.journal_id = aj.id
           where  aml.date <  %s and  aa.code  in %s
           and aml.company_id =%s
            group by aa.code)   opening 
			
			full join
			
			( select 
        aml.date as accounting_date,
        aml.date_maturity as voucher_date,
        aml.name vourcher_name, 
        aa.code,
        ( select array_agg(ab.code) from account_move_line a left join account_account ab on ab.id = a.account_id 
        where a.move_id = aml.move_id and a.account_id !=aml.account_id  group by ab.code limit 1) counter_part_code,
        aml.credit,
        aml.name as aml_name,
        aml.debit,
        aa.name, 
        rp.name as rp_name
        from account_move_line aml

        left join account_move am on am.id = aml.move_id 
        left join account_account aa on aa.id = aml.account_id
        left join account_move_line amls on amls.move_id = aml.move_id
        left join res_partner rp
        on aml.partner_id = rp.id
        where
        aa.code in %s
        and
        aml.date >=  %s and aml.date <= %s
        and aml.company_id =%s

        group by aa.code,aa.name, aml.debit, aml.credit,aml.name,aml.date,counter_part_code,voucher_date,rp.name

        order by aa.code, aml.date
        ) incurred
        on incurred.code = opening.code
             """
                    ,(start_date,account_ids,company_id,account_ids,start_date,end_date,company_id)
                )
        self.account_cash = self.env.cr.fetchall() 
        docs = []
        code= ''
        _item=[]
        ob=0
        record = []
        group = []
        _index =0 
        for item in  self.account_cash:
            _index += 1
            if item[3] != code:
                if len(group)>0:
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
                group = []
                group.append(item)
                code = item[3]
                ob=item[5]-item[6]
                if _index >= len(self.account_cash):
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
            else:
                group.append(item)
                if _index >= len(self.account_cash):
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
    
          
        return{
                'doc_ids':data['ids'],
                'doc_model':data['model'],
                'start_date':start_date,
                'end_date':end_date,
                'docs':docs,
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
    @staticmethod
    def to_tupe(str,order):
        tupe=[]
        length = len(str) -1
        for record in str[order:length].split(","):
                if record.strip().isdigit() == True:
                    tupe.append(record.strip())
        return tupe
                

         
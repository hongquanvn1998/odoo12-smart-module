from odoo import api,models,fields
from datetime import datetime
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
from collections import Counter
from odoo.exceptions import ValidationError

class ReportBusiness(models.TransientModel):
    _name = 'account.business.activities'
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
    data_from = fields.Boolean('Lấy dữ liệu từ BCTC đã lập')
    not_display = fields.Boolean('Không hiển thị các chỉ tiêu có số liệu = 0')
    acc_business_data = fields.Char('Name', size=256)
    file_name = fields.Binary('File excel', readonly=True)


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
        else:
            self.start_date = str(datetime.today().replace(day=1,month=10))
            self.end_date = str(datetime.today().replace(day=31,month=12))
        return  {'start_date': self.start_date, 'end_date': self.end_date}

    
    
    @api.multi
    def get_info (self):
        data ={
            'ids': self.ids,
            'model': self._name,
            'form': {
                'filter_date' :self.filter_date,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'data_from':self.data_from,
                'not_display':self.not_display,
            },
        }


        return self.env.ref('smart_invoice.business_activities').report_action(self, data=data)
        

    def export_excel(self):
        path='../home/export/'        
        self.env.cr.execute(
         """
                select  (case when opening.code is not null then opening.code when opening.code is null then incurred.code end ) code , 
                 (case when opening.name is not null then opening.name when opening.name is null then incurred.name end ) account_name , 
                 COALESCE (opening.debit, 0) opening_debit,  
                 COALESCE (opening.credit,0) opening_credit,
                 (select max(debit) from unnest(array[0, COALESCE (opening.debit,0)+COALESCE (incurred.debit,0)- COALESCE (incurred.credit,0) - COALESCE (opening.credit,0)]) debit  )  close_debit,
                 (select max(credit) from unnest(array[0,COALESCE (opening.credit,0)+COALESCE (incurred.credit,0)- COALESCE (incurred.debit,0) - COALESCE (opening.debit,0)]) credit  )  close_credit,  
                 incurred.date date
                 from
                 (select  
                 aa.code,aa.name, sum(aml.debit) debit, sum(aml.credit) credit
                 from  
                 account_move_line aml   
                 left join account_account aa on aa.id = aml.account_id 
                 where  
                 aml.DATE <  %s
                 group by aa.code, aa.name 
                 order by aa.code ) opening
                 full join
                 (
                 select 
                 aa.code,aa.name, sum(aml.debit) debit, sum(aml.credit) credit,MAX(aml.date) date
                 from 
                 account_move_line aml   
                 left join account_account aa on aa.id = aml.account_id
                 where 
                 aml.Date >= %s and aml.Date <= %s
                 group by aa.code,aa.name 
                 order by aa.code ) incurred 
                 on opening.code = incurred.code 
            """ ,
            (self.start_date, self.start_date, self.end_date)
        )
        self.acc_business = self.env.cr.fetchall()
        ic_511 = 0
        oc_511 = 0
        qw_01 = []
        
        ic_521 = 0
        oc_521 = 0
        qw_02 = []
        
        ic_632 = 0
        oc_632 = 0
        qw_11 =[]

        id_515 = 0
        od_515 = 0
        qw_21 = []
        
        oc_635 = 0
        ic_635 = 0
        qw_22 = []

        oc_641 = 0
        ic_641 = 0
        qw_25 = []
        
        oc_642 = 0
        ic_642 = 0
        qw_26 = []

        od_711 = 0
        id_711 = 0
        qw_31 = []

        oc_811 = 0
        ic_811 = 0
        qw_32 = []

        oc_8211 = 0
        ic_8211 = 0
        qw_51 = []

        oc_8212 = 0
        ic_8212 = 0
        qw_52 = []

        for item in self.acc_business:
         
            if item[0] == '5111':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5112':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5113':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5114':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5117':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5118':
                oc_511 += item[3]
                ic_511 +=item[5]
         
            if item[0] == '5211':
                oc_521 += item[3]
                ic_521 +=item[5]
            if item[0] == '5212' :
                oc_521 += item[3]
                ic_521 +=item[5]
            if item[0] == '5213':
                oc_521 += item[3]
                ic_521 +=item[5]

            if item[0] == '632':
                oc_632 += item[3]
                ic_632 += item[5]
            if item[0] == '515':
                od_515 = item[2]
                id_515 = item[4]
            if item[0] == '635':
                oc_635 += item[3]
                ic_635 += item[5]

            if item[0] == '6411':
                oc_641 += item[3]
                ic_641 += item[5]
                 
            if item[0] == '6412':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6413':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6414':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6415':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6417':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6418':
                oc_641 += item[3]
                ic_641 += item[5]

            if item[0] == '6421':
                oc_642 += item[3]
                ic_642 += item[5]
                 
            if item[0] == '6422':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6423':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6424':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6425':
                oc_642 += item[3]
                ic_642 += item[5]

            if item[0] == '6426':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6427':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6428':
                oc_642 += item[3]
                ic_642 += item[5]

            if item[0] == '711':
                od_711 += item[2]
                id_711 += item[4]

            
            if item[0] == '811':
                oc_811 += item[3]
                ic_811 += item[5]

            if item[0] == '8211':
                oc_8211 += item[3]
                ic_8211 += item[5]
                
            if item[0] == '8212':
                oc_8212 += item[3]
                ic_8212 += item[5]

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
        style12 = xlwt.easyxf('font: name Times New Roman,height 260;align: horiz center;', num_format_str='dd-mm-yyyy')
        style13 = xlwt.easyxf('font: name Times New Roman,height 260;align: horiz left;')
        
        sheet = workbook.add_sheet(self._name)
        
        c=7
        sheet.write_merge(2, 4, 4, 23, 'BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH', style8)
        sheet.write_merge(5, 6, 4, 23, 'Năm : %s' %(self.start_date), style10) 
        sheet.write_merge(c, c+1, 1, 13, 'Chỉ tiêu', style0)
        sheet.write_merge(c, c+1, 14, 16, 'Mã số', style0)
        sheet.write_merge(c, c+1, 17, 19, 'Thuyết minh', style0)
        sheet.write_merge(c, c+1, 24, 27, 'Số đầu kỳ', style0)
        sheet.write_merge(c, c+1, 20, 23, 'Số cuối kỳ', style0)
        
        # go
        sheet.write_merge(c+2, c+2, 1, 13, '1.Doanh thu bán hàng và cung cấp dịch vụ', style13)
        sheet.write_merge(c+2, c+2, 14, 16, '01', style10)
        sheet.write_merge(c+2, c+2, 17, 19, 'VII.1', style10)
        sheet.write_merge(c+2, c+2, 20, 23, oc_511, style10)
        sheet.write_merge(c + 2, c + 2, 24, 27, ic_511, style10)
        
        sheet.write_merge(c+3, c+3, 1, 13, '2.Các khoản giảm trừ doanh thu', style13)
        sheet.write_merge(c+3, c+3, 14, 16, '02', style10)
        sheet.write_merge(c+3, c+3, 17, 19, 'VII.2', style10)
        sheet.write_merge(c+3, c+3, 20, 23, oc_521, style10)
        sheet.write_merge(c + 3, c + 3, 24, 27, ic_521, style10)
        
        sheet.write_merge(c+4, c+4, 1, 13, '3.Doanh thu thuần về bán hàng và cung cấp dịch vụ (10 = 01 - 02)', style13)
        sheet.write_merge(c+4, c+4, 14, 16, '10', style10)
        sheet.write_merge(c + 4, c + 4, 17, 19, '', style10)
        qwo_10=oc_511-oc_521
        qwi_10= ic_511-ic_521
        sheet.write_merge(c+4, c+4, 20, 23, qwo_10, style10)
        sheet.write_merge(c+4, c + 4, 24, 27, qwi_10, style10)
        
        sheet.write_merge(c+5, c+5, 1, 13, '4.Giá vốn hàng bán', style13)
        sheet.write_merge(c+5, c+5, 14, 16, '11', style10)
        sheet.write_merge(c+5, c+5, 17, 19, 'VII.3', style10)
        sheet.write_merge(c+5, c+5, 20, 23, oc_632, style10)
        sheet.write_merge(c+5, c+5, 24, 27, ic_632, style10)
        
        sheet.write_merge(c+6, c+6, 1, 13, '5.Lợi nhuận gộp về bán hàng và cung cấp dịch vụ (20 = 10 -11)', style13)
        sheet.write_merge(c+6, c+6, 14, 16, '20', style10)
        sheet.write_merge(c + 6, c + 6, 17, 19, '', style10)
        qwo_20 = qwo_10 - oc_632
        qwi_20 = qwi_10-ic_632
        sheet.write_merge(c+6, c+6, 20, 23, qwo_20, style10)
        sheet.write_merge(c+6, c+6, 24, 27, qwi_20, style10)
        
        sheet.write_merge(c+7, c+7, 1, 13, '6.Doanh thu hoạt động tài chính', style13)
        sheet.write_merge(c+7, c+7, 14, 16, '21', style10)
        sheet.write_merge(c+7, c+7, 17, 19, 'VII.4', style10)
        sheet.write_merge(c+7, c+7, 20, 23,od_515 , style10)
        sheet.write_merge(c+7, c+7, 24, 27,id_515 , style10)
        
        sheet.write_merge(c+8, c+8, 1, 13, '7.Chi phí tài chính', style13)
        sheet.write_merge(c+8, c+8, 14, 16, '22', style10)
        sheet.write_merge(c+8, c+8, 17, 19, 'VII.5', style10)
        sheet.write_merge(c+8, c+8, 20, 23, oc_635, style10)
        sheet.write_merge(c+8, c+8, 24, 27, ic_635, style10)
        
        sheet.write_merge(c+9, c+9, 1, 13, '- Trong đó: Chi phí lãi vay', style13)
        sheet.write_merge(c+9, c+9, 14, 16, '23', style10)
        sheet.write_merge(c+9, c+9, 17, 19, '', style10)
        sheet.write_merge(c+9, c+9, 20, 23, '', style10)
        sheet.write_merge(c+9, c+9, 24, 27, '', style10)
        
        sheet.write_merge(c+10, c+10, 1, 13, '8.Chi phí bán hàng', style13)
        sheet.write_merge(c+10, c+10, 14, 16, '25', style10)
        sheet.write_merge(c+10, c+10, 17, 19, 'VII.8', style10)
        sheet.write_merge(c+10, c+10, 20, 23, oc_641, style10)
        sheet.write_merge(c+10, c+10, 24, 27, ic_641, style10)
        
        sheet.write_merge(c+11, c+11, 1, 13, '9.Chi phí quản lý doanh nghiệp', style13)
        sheet.write_merge(c+11, c+11, 14, 16, '25', style10)
        sheet.write_merge(c+11, c+11, 17, 19, 'VII.8', style10)
        sheet.write_merge(c+11, c+11, 20, 23, oc_642, style10)
        sheet.write_merge(c+11, c+11, 24, 27, ic_642, style10)

        sheet.write_merge(c+12, c+12, 1, 13, '10.Lợi nhuận thuần từ hoạt động kinh doanh (30 = 20 + (21 - 22) - 25 - 26)', style13)
        sheet.write_merge(c+12, c+12, 14, 16, '30', style10)
        sheet.write_merge(c + 12, c + 12, 17, 19, '', style10)
        qwo_30= qwo_10 - oc_632 + od_515- oc_635 - oc_641 -oc_642
        qwi_30= qwi_10 - ic_632 + od_515- oc_635 - oc_641 -oc_642
        sheet.write_merge(c+12, c+12, 20, 23, qwo_30, style10)
        sheet.write_merge(c+12, c+12, 24, 27, qwi_30, style10)

        sheet.write_merge(c+13, c+13, 1, 13, '11.Thu nhập khác', style13)
        sheet.write_merge(c+13, c+13, 14, 16, '31', style10)
        sheet.write_merge(c+13, c+13, 17, 19, 'VII.6', style10)
        sheet.write_merge(c+13, c+13, 20, 23, od_711, style10)
        sheet.write_merge(c+13, c+13, 24, 27, id_711, style10)

        sheet.write_merge(c+14, c+14, 1, 13, '12.Chi phí khác', style13)
        sheet.write_merge(c+14, c+14, 14, 16, '32', style10)
        sheet.write_merge(c+14, c+14, 17, 19, 'VII.7', style10)
        sheet.write_merge(c+14, c+14, 20, 23, oc_811, style10)
        sheet.write_merge(c+14, c+14, 24, 27, ic_811, style10)

        sheet.write_merge(c+15, c+15, 1, 13, '13.Lợi nhuận khác (40 = 31 - 32)', style13)
        sheet.write_merge(c+15, c+15, 14, 16, '40', style10)
        sheet.write_merge(c + 15, c + 15, 17, 19, '', style10)
        qwo_40=od_711-oc_811
        qwi_40=id_711-ic_811
        sheet.write_merge(c+15, c+15, 20, 23, qwo_40, style10)
        sheet.write_merge(c+15, c+15, 24, 27, qwi_40, style10)

        sheet.write_merge(c+16, c+16, 1, 13, '14.Tổng lợi nhuận kế toán trước thuế (50 = 30 + 40)', style13)
        sheet.write_merge(c+16, c+16, 14, 16, '50', style10)
        sheet.write_merge(c + 16, c + 16, 17, 19, '', style10)
        qwo_50 = qwo_40 + qwo_10 - oc_632 + od_515- oc_635 - oc_641 -oc_642
        qwi_50= qwi_40 + qwi_10 - ic_632 + od_515- oc_635 - oc_641 -oc_642
        sheet.write_merge(c+16, c+16, 20, 23,qwo_50, style10)
        sheet.write_merge(c+16, c+16, 24, 27, qwi_50, style10)

        sheet.write_merge(c+17, c+17, 1, 13, '15.Chi phí thuế TNDN hiện hành', style13)
        sheet.write_merge(c+17, c+17, 14, 16, '51', style10)
        sheet.write_merge(c+17, c+17, 17, 19, 'VII.10', style10)
        sheet.write_merge(c+17, c+17, 20, 23,oc_8211 , style10)
        sheet.write_merge(c+17, c+17, 24, 27, ic_8211, style10)
        
        sheet.write_merge(c+18, c+18, 1, 13, '16.Chi phí thuế TNDN hoãn lại', style13)
        sheet.write_merge(c+18, c+18, 14, 16, '52', style10)
        sheet.write_merge(c+18, c+18, 17, 19, 'VII.11', style10)
        sheet.write_merge(c+18, c+18, 20, 23, oc_8212, style10)
        sheet.write_merge(c+18, c+18, 24, 27, ic_8212, style10)
        
        sheet.write_merge(c+19, c+19, 1, 13, '17.Lợi nhuận sau thuế thu nhập doanh nghiệp(60 = 50 - 51 - 52)', style13)
        sheet.write_merge(c+19, c+19, 14, 16, '60', style10)
        sheet.write_merge(c+19, c+19, 17, 19, '', style10)
        sheet.write_merge(c+19, c+19, 20, 23, qwo_40 + qwo_10 - oc_632 + od_515- oc_635 - oc_641 -oc_642-oc_8211-oc_8212, style10)
        sheet.write_merge(c+19, c+19, 24, 27, qwi_40 + qwi_10 - ic_632 + od_515- oc_635 - oc_641 -oc_642-ic_8211-ic_8212, style10)

        
        sheet.write_merge(c+20, c+20, 1, 13, '18.Lãi cơ bản trên cổ phiếu(*)', style13)
        sheet.write_merge(c+20, c+20, 14, 16, '70', style10)
        sheet.write_merge(c+20, c+20, 17, 19, '', style10)
        sheet.write_merge(c+20, c+20, 20, 23, '', style10)
        sheet.write_merge(c+20, c+20, 24, 27, '', style10)


        
        sheet.write_merge(c+21, c+21, 1, 13, '19.Lãi suy giảm trên cổ phiếu(*)', style13)
        sheet.write_merge(c+21, c+21, 14, 16, '71', style10)
        sheet.write_merge(c+21, c+21, 17, 19, '', style10)
        sheet.write_merge(c+21, c+21, 20, 23, '', style10)
        sheet.write_merge(c+21, c+21, 24, 27, '', style10)

        # end
                            
        filename = ('%s'+ '.xls') %(self._name)
        workbook.save(r'%s%s' %(path,filename))
        fp = open(r'%s%s' %(path,filename), "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)                                                 
                    
# Files actions         
        attach_vals = {
                'acc_business_data': self._name + '.xls',
                'file_name': out,
            }
            
        act_id = self.env['account.business.activities'].create(attach_vals)
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

class BusinessActivitiesView(models.AbstractModel):
    _name='report.smart_invoice.business_activities_display'

    @api.model
    def _get_report_values(self,docids,data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= end_date + ' 23:59:59'
        filter_date=data['form']['filter_date']

        self.env.cr.execute(
            """
            select 
		(case 
		 when opening.code is not null then opening.code else incurred.code
		 end) code,
		incurred.counter_part_code, 
		COALESCE (opening.debit, 0) opening_debit,  
		COALESCE (opening.credit,0) opening_credit,
        (select max(debit) from unnest(array[0, COALESCE (opening.debit,0)+COALESCE (incurred.debit,0)- COALESCE (incurred.credit,0) - COALESCE (opening.credit,0)]) debit  )  close_debit,
        (select max(credit) from unnest(array[0,COALESCE (opening.credit,0)+COALESCE (incurred.credit,0)- COALESCE (incurred.debit,0) - COALESCE (opening.debit,0)]) credit  )  close_credit 
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
            left join account_account aa
            on aa.id= aml.account_id
           where  aml.date <  %s
            group by aa.code)   opening 
			full join
			( select 
        aa.code,
        ( select ab.code from account_move_line a left join account_account ab on ab.id = a.account_id 
        where a.move_id = aml.move_id and a.account_id !=aml.account_id  group by ab.code limit 1) counter_part_code,
        SUM(aml.credit) as credit,
        SUM(aml.debit) as debit
        from account_move_line aml
        left join account_account aa on aa.id = aml.account_id
        where
        aml.date >=  %s and aml.date <=  %s
        group by  counter_part_code,aa.code
        ) incurred
        on incurred.code = opening.code
		order by code
            """ ,
            (start_date, start_date, end_date)
        )
        self.acc_business = self.env.cr.fetchall()
        ic_511 = 0
        oc_511 = 0
        qw_01 = []
        
        ic_521 = 0
        oc_521 = 0
        qw_02 = []
        
        ic_632 = 0
        oc_632 = 0
        qw_11 =[]

        id_515 = 0
        od_515 = 0
        qw_21 = []
        
        oc_635 = 0
        ic_635 = 0
        qw_22 = []

        oc_641 = 0
        ic_641 = 0
        qw_25 = []
        
        oc_642 = 0
        ic_642 = 0
        qw_26 = []

        od_711 = 0
        id_711 = 0
        qw_31 = []

        oc_811 = 0
        ic_811 = 0
        qw_32 = []

        oc_8211 = 0
        ic_8211 = 0
        qw_51 = []

        oc_8212 = 0
        ic_8212 = 0
        qw_52 = []
        
        
        
        

        for item in self.acc_business:
         
            if item[0] == '5111':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5112':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5113':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5114':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5117':
                oc_511 += item[3]
                ic_511 +=item[5]
            if item[0] == '5118':
                oc_511 += item[3]
                ic_511 +=item[5]
         
            if item[0] == '5211':
                oc_521 += item[3]
                ic_521 +=item[5]
            if item[0] == '5212' :
                oc_521 += item[3]
                ic_521 +=item[5]
            if item[0] == '5213':
                oc_521 += item[3]
                ic_521 +=item[5]

            if item[0] == '632':
                oc_632 += item[3]
                ic_632 += item[5]
            if item[0] == '515':
                od_515 = item[2]
                id_515 = item[4]
            if item[0] == '635':
                oc_635 += item[3]
                ic_635 += item[5]

            if item[0] == '6411':
                oc_641 += item[3]
                ic_641 += item[5]
                 
            if item[0] == '6412':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6413':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6414':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6415':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6417':
                oc_641 += item[3]
                ic_641 += item[5]
                
            if item[0] == '6418':
                oc_641 += item[3]
                ic_641 += item[5]

            if item[0] == '6421':
                oc_642 += item[3]
                ic_642 += item[5]
                 
            if item[0] == '6422':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6423':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6424':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6425':
                oc_642 += item[3]
                ic_642 += item[5]

            if item[0] == '6426':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6427':
                oc_642 += item[3]
                ic_642 += item[5]
                
            if item[0] == '6428':
                oc_642 += item[3]
                ic_642 += item[5]

            if item[0] == '711':
                od_711 += item[2]
                id_711 += item[4]

            
            if item[0] == '811':
                oc_811 += item[3]
                ic_811 += item[5]

            if item[0] == '8211':
                oc_8211 += item[3]
                ic_8211 += item[5]
                
            if item[0] == '8212':
                oc_8212 += item[3]
                ic_8212 += item[5]


        qw_01.append({
            'ic_511': ic_511,
            'oc_511':oc_511
                    })

        qw_02.append({
            'oc_521': oc_521,
            'ic_521': ic_521
            
        })

        qw_11.append({
            'oc_632': oc_632,
            'ic_632': ic_632
        })

        qw_21.append({
            'od_515': od_515,
            'id_515' :id_515
        })

        qw_22.append({
            'oc_635': oc_635,
            'ic_635': ic_635
        })
        qw_25.append({
            'oc_641': oc_641,
            'ic_641':ic_641
        })

        qw_26.append({
            'oc_642': oc_642,
            'ic_642': ic_642
        })
        qw_31.append({
            'od_711': od_711,
            'id_711':id_711
        })
        qw_32.append({
            'oc_811': oc_811,
            'ic_811': ic_811,
        })

        qw_51.append({
            'oc_8211': oc_8211,
            'ic_8211':ic_8211
        })

        qw_52.append({
            'oc_8212': oc_8212,
            'ic_8212':ic_8212
        })
        return{
            'doc_ids':data['ids'],
            'doc_model':data['model'],
            'start_date':start_date,
            'end_date': end_date,
            'qw_01': qw_01,
            'qw_02': qw_02,
            'qw_11': qw_11,
            'qw_21': qw_21,
            'qw_22': qw_22,
            'qw_25': qw_25,
            'qw_26': qw_26,
            'qw_31': qw_31,
            'qw_32': qw_32,
            'qw_51': qw_51,
            'qw_52': qw_52,
            
            
            
        }
             
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

class ReportCashFlows(models.TransientModel):
    _name = 'account.cash.flows'
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
    cash_flow_data = fields.Char('Name', size=256)
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
        if 9 < currentMonth <= 12 :
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
        return self.env.ref('smart_invoice.cash_flows').report_action(self, data=data)
    def export_excel(self):
                path='../home/export/'          
                # path='../excel/'          
      
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
                self.cash_flow = self.env.cr.fetchall()

                oc_01 = 0
                ic_01 = 0
                
                od_02= 0
                id_02 = 0
                
                od_03 = 0
                id_03 = 0
                
                od_04 = 0
                id_04 = 0
                
                od_05 = 0
                id_05 = 0
                
                oc_06 = 0
                ic_06 = 0

                od_07 = 0
                id_07 = 0
                

                od_21 = 0
                id_21 = 0

                od_22 = 0
                id_22 = 0

                od_23 = 0
                id_23 = 0


                oc_24 = 0
                ic_24 = 0

                od_25 = 0
                id_25 = 0

                oc_26 = 0
                ic_26 = 0

                oc_27 = 0
                ic_27 = 0

                oc_31 = 0
                ic_31 = 0

                od_32 = 0
                id_32 = 0

                oc_33 = 0
                ic_33 = 0

                od_34 = 0
                id_34 = 0

                od_35 = 0
                id_35 = 0

                od_36 = 0
                id_36 = 0

                od_60 = 0
                id_60=0

                oc_61 = 0
                ic_61 = 0
                
                qwo_20 = 0
                qwi_20 = 0

                qwo_30= 0
                qwi_30 = 0

                qwi_40 = 0
                qwo_40 = 0

                qwi_50= 0
                qwo_50= 50

                qw0_71= 0
                qwi_71= 0


                isMoney = True
                _time = 2

                for item in self.cash_flow:
                    if item[0] == '511':
                        oc_01 += item[3]
                        ic_01 += item[5]

                    if item[0] == '3331':
                        oc_01 += item[3]
                        ic_01 += item[5]

                    if item[0] == '131':
                        oc_01 += item[3]
                        ic_01 += item[5]

                    if item[0] == '1211':
                        oc_01 += item[3]
                        ic_01 += item[5]

                    if item[0] == '1212':
                        oc_01 += item[3]
                        ic_01 += item[5]

                    if item[0] == '1218':
                        oc_01 += item[3]
                        ic_01 += item[5]

                    if item[0] == '331' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '151' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '152' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1531' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1532' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1533' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1534' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '154' :
                        od_02 += item[2]
                        id_02 += item[4]
                            
                    if item[0] == '1551' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1557' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1561' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1562' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '1567' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '157' :
                        od_02 += item[2]
                        id_02 += item[4]

                    if item[0] == '158' :
                        od_02 += item[2]
                        id_02 += item[4]


                    if item[0] == '3341':
                        od_03 += item[2]
                        id_03 += item[4]

                    if item[0] == '3348':
                        od_03 += item[2]
                        id_03 += item[4]

                    if item[0] == '335':
                        od_04 += item[2]
                        id_04 += item[4]


                    if item[0] == '635':
                        od_04 += item[2]
                        id_04 += item[4]           

                    if item[0] == '242':
                        od_04 += item[2]
                        id_04 += item[4]            

                    if item[0] == '3334':
                        od_05 += item[2]
                        id_05 += item[4]

                    if item[0] == '711':
                        oc_06 += item[3]
                        ic_06 += item[5]


                    if item[0] == '1331':
                        oc_06 += item[3]
                        ic_06 += item[5]

                    if item[0] == '1332':
                        oc_06 += item[3]
                        ic_06 += item[5]

                    if item[0] == '141':
                        oc_06 += item[3]
                        ic_06 += item[5]   

                    if item[0] == '244':
                        oc_06 += item[3]
                        ic_06 += item[5]

                    if item[0] == '811':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '1611':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '1612':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '244':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3331':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '33311':
                        od_07 += item[2]
                        id_07 += item[4]                

                    if item[0] == '33312':
                        od_07 += item[2]
                        id_07 += item[4]                       

                    if item[0] == '3332':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3333':
                        od_07 += item[2]
                        id_07 += item[4]


                    if item[0] == '3334':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3335':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3336':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3337':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '33381':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '33382':
                        od_07 += item[2]
                        id_07 += item[4]


                    if item[0] == '3339':
                        od_07 += item[2]
                        id_07 += item[4]
                        
                    if item[0] == '3381':
                        od_07 += item[2]
                        id_07 += item[4]
                

                    if item[0] == '3382':
                        od_07 += item[2]
                        id_07 += item[4]


                    if item[0] == '344':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3521':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3522':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3523':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3524':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3531':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3532':
                        od_07 += item[2]
                        id_07 += item[4]
                
                    if item[0] == '3533':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3534':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3561':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '3562':
                        od_07 += item[2]
                        id_07 += item[4]

                    if item[0] == '2111':
                        od_21 += item[2]
                        id_21 += item[4]

                    if item[0] == '2112':
                        od_21 += item[2]
                        id_21 += item[4]                                                                              
                        
                    if item[0] == '2113':
                        od_21 += item[2]
                        id_21 += item[4]

                    if item[0] == '2114':
                        od_21 += item[2]
                        id_21 += item[4]
                                                                                                    
                    if item[0] == '2115':
                        od_21 += item[2]
                        id_21 += item[4]

                    if item[0] == '2118':
                        od_21 += item[2]
                        id_21 += item[4]
                        
                    if item[0] == '2131':
                        od_21 += item[2]
                        id_21 += item[4]
                        
                    if item[0] == '2132':
                        od_21 += item[2]
                        id_21 += item[4]                   
                    if item[0] == '2133':
                        od_21 += item[2]
                        id_21 += item[4]  
                    if item[0] == '2134':
                        od_21 += item[2]
                        id_21 += item[4]  

                    if item[0] == '2135':
                        od_21 += item[2]
                        id_21 += item[4]
                        
                    if item[0] == '2136':
                        od_21 += item[2]
                        id_21 += item[4]
                        
                    if item[0] == '2138':
                        od_21 += item[2]
                        id_21 += item[4]

                    if item[0] == '217':
                        od_21 += item[2]
                        id_21 += item[4]

                    if item[0]=='2411':
                        od_21 += item[2]
                        id_21 += item[4]

                    if item[0]=='2412':
                        od_21 += item[2]
                        id_21 += item[4]

                    if item[0]=='2413':
                        od_21 += item[2]
                        id_21 += item[4]
                    if item[0] == '3411':
                        od_21 += item[2]
                        id_21 += item[4]

                    # 2xx o day
                    if item[0] == '632':
                        od_22 += item[2]
                        id_22 += item[4]
                    
                    if item[0] == '811':
                        od_22 += item[2]
                        id_22 += item[4]

                    if item[0] == '1281' :
                        od_23 += item[2]
                        id_23 += item[4]

                    if item[0] == '1282' :
                        od_23 += item[2]
                        id_23 += item[4]

                    if item[0] == '1288':
                        od_23 += item[2]
                        id_23 += item[4]

                    if item[0] == '171':
                        od_23 += item[2]
                        id_23 += item[4]

                    if item[0] == '1281' :
                        oc_24 += item[3]
                        ic_24 += item[5]

                    if item[0] == '1282' :
                        oc_24 += item[3]
                        ic_24 += item[5]

                    if item[0] == '1288':
                        oc_24 += item[3]
                        ic_24 += item[5]

                    if item[0] == '171':
                        oc_24 += item[3]
                        ic_24 += item[5]
                    
                    if item[0] == '221':
                        od_25 += item[2]
                        id_25 += item[4]

                    if item[0] == '222':
                        od_25 += item[2]
                        id_25 += item[4]

                    if item[0] == '2281':
                        od_25 += item[2]
                        id_25 += item[4]

                    if item[0] == '331':
                        od_25 += item[2]
                        id_25 += item[4]


                    
                    if item[0] == '221':
                        oc_26 += item[3]
                        ic_26 += item[5]

                    if item[0] == '222':
                        oc_26 += item[3]
                        ic_26 += item[5]

                    if item[0] == '2281':
                        oc_26 += item[3]
                        ic_26 += item[5]

                    if item[0] == '331':
                        oc_26 += item[3]
                        ic_26 += item[5]


                    if item[0] == '515':
                        oc_27 += item[3]
                        ic_27 += item[5]

                    # end

                    if item[0] == '41111':
                        oc_31 += item[3]
                        ic_31 += item[5]
            
                    if item[0] == '41112':
                        oc_31 += item[3]
                        ic_31 += item[5]    
                
                    if item[0] == '4112':
                        oc_31 += item[3]
                        ic_31 += item[5]            

                    if item[0] == '4113':
                        oc_31 += item[3]
                        ic_31 += item[5]

                    if item[0] == '4118':
                        oc_31 += item[3]
                        ic_31 += item[5]



                    if item[0] == '41111':
                        od_32 += item[2]
                        id_32 += item[4]
            
                    if item[0] == '41112':
                        od_32 += item[2]
                        id_32 += item[4]    
                
                    if item[0] == '4112':
                        od_32 += item[2]
                        id_32 += item[4]            

                    if item[0] == '4113':
                        od_32 += item[2]
                        id_32 += item[4]

                    if item[0] == '4118':
                        od_32 += item[2]
                        id_32 += item[4]

                    
                    if item[0] == '419':
                        od_32 += item[2]
                        id_32 += item[4]     

                    if item[0] == '3411':
                        oc_33 += item[3]
                        ic_33 += item[5]     
                        

                    if item[0] == '3431':
                        oc_33 += item[3]
                        ic_33 += item[5]     

                    if item[0] == '3432':
                        oc_33 += item[3]
                        ic_33 += item[5]


                    if item[0] == '41112':
                        oc_33 += item[3]
                        ic_33 += item[5]
                        
                    if item[0] == '3411':
                        od_34 += item[2]
                        id_34 += item[4]     
                        

                    if item[0] == '3431':
                        od_34 += item[2]
                        id_34 += item[4]     

                    if item[0] == '3432':
                        od_34 += item[2]
                        id_34 += item[4]


                    if item[0] == '41112':
                        od_34 += item[2]
                        id_34 += item[4]     



                    if item[0] == '3412':
                        od_35 += item[2]
                        id_35 += item[4]    


                    if item[0] == '4211':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '4212':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3381':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3382':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3383':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3384':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3385':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3386':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3387':
                        od_36 += item[2]
                        id_36 += item[4]

                    if item[0] == '3388':
                        od_36 += item[2]
                        id_36 += item[4]




                    if item[0] == '1111':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1112':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1113':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1121':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1122':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1123':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1131':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1132':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1281' :
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '1288':
                        od_60 += item[2]
                        id_60 += item[4]

                    if item[0] == '4131':
                        oc_61 += item[3]
                        ic_61 += item[5]



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
                style14 = xlwt.easyxf('font: name Times New Roman ,bold on,height 260;align: horiz left;')
                
                sheet = workbook.add_sheet(self._name)
                
                c=7
                sheet.write_merge(2, 4, 4, 23, 'BÁO CÁO TỔNG HỢP DÒNG TIỀN', style8)
                sheet.write_merge(5, 6, 4, 23, 'Từ ngày  : %s Đến ngày : %s' %(self.start_date, self.start_date), style12) 
                sheet.write_merge(c, c+1, 1, 13, 'Chỉ tiêu', style0)
                sheet.write_merge(c, c+1, 14, 16, 'Mã số', style0)
                sheet.write_merge(c, c+1, 17, 19, 'Thuyết minh', style0)
                sheet.write_merge(c, c+1, 20, 23, 'Kỳ này', style0)
                sheet.write_merge(c, c+1, 24, 27, 'Kỳ trước', style0)
                
                # go
                sheet.write_merge(c+2, c+2, 1, 13, 'I. Lưu chuyển tiền từ hoạt động kinh doanh', style14)
                sheet.write_merge(c+2, c+2, 14, 16, '', style10)
                sheet.write_merge(c+2, c+2, 17, 19, '', style10)
                sheet.write_merge(c+2, c+2, 20, 23, '', style10)
                sheet.write_merge(c + 2, c+2, 24, 27, '', style10)
                
                sheet.write_merge(c+3, c+3, 1, 13, '1. Tiền thu từ bán hàng, cung cấp dịch vụ và doanh thu khác', style13)
                sheet.write_merge(c+3, c+3, 14, 16, '01', style10)
                sheet.write_merge(c+3, c+3, 17, 19, '', style10)
                sheet.write_merge(c+3, c+3, 20, 23, oc_01, style10)
                sheet.write_merge(c+3, c+3, 24, 27, ic_01, style10)
                
                sheet.write_merge(c+4, c+4, 1, 13, '2. Tiền chi trả cho người cung cấp hàng hóa và dịch vụ	', style13)
                sheet.write_merge(c+4, c+4, 14, 16, '02', style10)
                sheet.write_merge(c+4, c+4, 17, 19, '', style10)
                sheet.write_merge(c+4, c+4, 20, 23, od_02, style10)
                sheet.write_merge(c+4, c + 4, 24, 27, id_02, style10)
                
                sheet.write_merge(c+5, c+5, 1, 13, '3. Tiền chi trả cho người lao động', style13)
                sheet.write_merge(c+5, c+5, 14, 16, '03', style10)
                sheet.write_merge(c+5, c+5, 17, 19, '', style10)
                sheet.write_merge(c+5, c+5, 20, 23, od_03, style10)
                sheet.write_merge(c+5, c+5, 24, 27, id_03, style10)
                
                sheet.write_merge(c+6, c+6, 1, 13, '4. Tiền lãi vay đã trả', style13)
                sheet.write_merge(c+6, c+6, 14, 16, '04', style10)
                sheet.write_merge(c+6, c+6, 17, 19, '', style10)
                sheet.write_merge(c+6, c+6, 20, 23, od_04, style10)
                sheet.write_merge(c+6, c+6, 24, 27, id_04, style10)
                
                sheet.write_merge(c+7, c+7, 1, 13, '5. Thuế thu nhập doanh nghiệp đã nộp', style13)
                sheet.write_merge(c+7, c+7, 14, 16, '05', style10)
                sheet.write_merge(c+7, c+7, 17, 19, '', style10)
                sheet.write_merge(c+7, c+7, 20, 23, od_05, style10)
                sheet.write_merge(c+7, c+7, 24, 27, id_05, style10)
                
                sheet.write_merge(c+8, c+8, 1, 13, '6. Tiền thu khác từ hoạt động kinh doanh', style13)
                sheet.write_merge(c+8, c+8, 14, 16, '06', style10)
                sheet.write_merge(c+8, c+8, 17, 19, '', style10)
                sheet.write_merge(c+8, c+8, 20, 23,oc_06 , style10)
                sheet.write_merge(c+8, c+8, 24, 27,ic_06 , style10)
                
                sheet.write_merge(c+9, c+9, 1, 13, '7. Tiền chi khác cho hoạt động kinh doanh', style13)
                sheet.write_merge(c+9, c+9, 14, 16, '07', style10)
                sheet.write_merge(c+9, c+9, 17, 19, '', style10)
                sheet.write_merge(c+9, c+9, 20, 23,od_07 , style10)
                sheet.write_merge(c+9, c+9, 24, 27, id_07, style10)

                qwo_20=oc_01 +od_02+od_03+od_04+od_05+oc_06+od_07
                qwi_20=ic_01 +id_02+id_03+id_04+id_05+ic_06+id_07

                sheet.write_merge(c+10, c+10, 1, 13, 'Lưu chuyển tiền thuần từ hoạt động kinh doanh', style14)
                sheet.write_merge(c+10, c+10, 14, 16, '20', style10)
                sheet.write_merge(c+10, c+10, 17, 19, '', style10)
                sheet.write_merge(c+10, c+10, 20, 23,qwo_20 , style10)
                sheet.write_merge(c+10, c+10, 24, 27,qwi_20 , style10)
                
                sheet.write_merge(c+11, c+11, 1, 13, 'II. Lưu chuyển tiền từ hoạt động đầu tư', style14)
                sheet.write_merge(c+11, c+11, 14, 16, '', style10)
                sheet.write_merge(c+11, c+11, 17, 19, '', style10)
                sheet.write_merge(c+11, c+11, 20, 23, '', style10)
                sheet.write_merge(c+11, c+11, 24, 27, '', style10)

                sheet.write_merge(c+12, c+12, 1, 13, '1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác', style13)
                sheet.write_merge(c+12, c+12, 14, 16, '21', style10)
                sheet.write_merge(c+12, c+12, 17, 19, '', style10)
                sheet.write_merge(c+12, c+12, 20, 23,od_21 , style10)
                sheet.write_merge(c+12, c+12, 24, 27, id_21, style10)

                sheet.write_merge(c+13, c+13, 1, 13, '2. Tiền thu từ thanh lý, nhượng bán TSCĐ và các tàu sản dài hạn khác', style13)
                sheet.write_merge(c+13, c+13, 14, 16, '22', style10)
                sheet.write_merge(c+13, c+13, 17, 19, '', style10)
                sheet.write_merge(c+13, c+13, 20, 23, od_22, style10)
                sheet.write_merge(c+13, c+13, 24, 27, id_22, style10)

                sheet.write_merge(c+14, c+14, 1, 13, '3. Tiền chi cho vay, mua các công cụ nợ của đơn vị khác', style13)
                sheet.write_merge(c+14, c+14, 14, 16, '23', style10)
                sheet.write_merge(c+14, c+14, 17, 19, '', style10)
                sheet.write_merge(c+14, c+14, 20, 23, od_23, style10)
                sheet.write_merge(c+14, c+14, 24, 27,id_23 , style10)

                sheet.write_merge(c+15, c+15, 1, 13, '4. Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác', style13)
                sheet.write_merge(c+15, c+15, 14, 16, '24', style10)
                sheet.write_merge(c+15, c+15, 17, 19, '', style10)
                sheet.write_merge(c+15, c+15, 20, 23, oc_24, style10)
                sheet.write_merge(c+15, c+15, 24, 27, ic_24, style10)

                sheet.write_merge(c+16, c+16, 1, 13, '5. Tiền chi đầu tư góp vốn vào đơn vị khác', style13)
                sheet.write_merge(c+16, c+16, 14, 16, '25', style10)
                sheet.write_merge(c+16, c+16, 17, 19, '', style10)
                sheet.write_merge(c+16, c+16, 20, 23, od_25, style10)
                sheet.write_merge(c+16, c+16, 24, 27, id_25, style10)

                sheet.write_merge(c+17, c+17, 1, 13, '6. Tiền thu hồi đầu tư góp vốn vào đơn vị khác', style13)
                sheet.write_merge(c+17, c+17, 14, 16, '26', style10)
                sheet.write_merge(c+17, c+17, 17, 19, '', style10)
                sheet.write_merge(c+17, c+17, 20, 23,oc_26 , style10)
                sheet.write_merge(c+17, c+17, 24, 27, ic_26, style10)
                
                sheet.write_merge(c+18, c+18, 1, 13, '7. Tiền thu lãi cho vay, cổ tức và lợi nhuận được chia', style13)
                sheet.write_merge(c+18, c+18, 14, 16, '27', style10)
                sheet.write_merge(c+18, c+18, 17, 19, '', style10)
                sheet.write_merge(c+18, c+18, 20, 23,oc_27 , style10)
                sheet.write_merge(c+18, c+18, 24, 27, ic_27, style10)
                
                qwo_30=od_21 +od_22 +od_23 +oc_24+od_25+oc_26 +oc_27
                qwi_30=id_21 +id_22 +id_23 +ic_24+id_25+ic_26 +ic_27

                sheet.write_merge(c+19, c+19, 1, 13, 'Lưu chuyển tiền thuần từ hoạt động đầu tư', style14)
                sheet.write_merge(c+19, c+19, 14, 16, '30', style10)
                sheet.write_merge(c+19, c+19, 17, 19, '', style10)
                sheet.write_merge(c+19, c+19, 20, 23,qwo_30 , style10)
                sheet.write_merge(c+19, c+19, 24, 27,qwi_30 , style10)

                
                sheet.write_merge(c+20, c+20, 1, 13, 'III. Lưu chuyển tiền từ hoạt động tài chính', style14)
                sheet.write_merge(c+20, c+20, 14, 16, '', style10)
                sheet.write_merge(c+20, c+20, 17, 19, '', style10)
                sheet.write_merge(c+20, c+20, 20, 23, '', style10)
                sheet.write_merge(c+20, c+20, 24, 27, '', style10)
                
                sheet.write_merge(c+21, c+21, 1, 13, '1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu', style13)
                sheet.write_merge(c+21, c+21, 14, 16, '31', style10)
                sheet.write_merge(c+21, c+21, 17, 19, '', style10)
                sheet.write_merge(c+21, c+21, 20, 23, oc_31, style10)
                sheet.write_merge(c+21, c+21, 24, 27, ic_31, style10)
                
                sheet.write_merge(c+22, c+22, 1, 13, '2. Tiền trả lại vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành', style13)
                sheet.write_merge(c+22, c+22, 14, 16, '32', style10)
                sheet.write_merge(c+22, c+22, 17, 19, '', style10)
                sheet.write_merge(c+22, c+22, 20, 23, od_32, style10)
                sheet.write_merge(c+22, c+22, 24, 27,id_32 , style10)
                
                sheet.write_merge(c+23, c+23, 1, 13, '3. Tiền vay ngắn hạn, dài hạn nhận được', style13)
                sheet.write_merge(c+23, c+23, 14, 16, '33', style10)
                sheet.write_merge(c+23, c+23, 17, 19, '', style10)
                sheet.write_merge(c+23, c+23, 20, 23, oc_33, style10)
                sheet.write_merge(c+23, c+23, 24, 27, ic_33, style10)

                sheet.write_merge(c+24, c+24, 1, 13, '4. Tiền trả nợ gốc vay', style13)
                sheet.write_merge(c+24, c+24, 14, 16, '34', style10)
                sheet.write_merge(c+24, c+24, 17, 19, '', style10)
                sheet.write_merge(c+24, c+24, 20, 23, od_34, style10)
                sheet.write_merge(c+24, c+24, 24, 27,id_34 , style10)
                
                sheet.write_merge(c+25, c+25, 1, 13, '5. Tiền trả nợ gốc thuê tài chính', style13)
                sheet.write_merge(c+25, c+25, 14, 16, '35', style10)
                sheet.write_merge(c+25, c+25, 17, 19, '', style10)
                sheet.write_merge(c+25, c+25, 20, 23, od_35, style10)
                sheet.write_merge(c+25, c+25, 24, 27,id_35 , style10)
                
                sheet.write_merge(c+26, c+26, 1, 13, '6. Cổ tức, lợi nhuận đã trả cho chủ sở hữu', style13)
                sheet.write_merge(c+26, c+26, 14, 16, '36', style10)
                sheet.write_merge(c+26, c+26, 17, 19, '', style10)
                sheet.write_merge(c+26, c+26, 20, 23,od_36 , style10)
                sheet.write_merge(c+26, c+26, 24, 27,id_36 , style10)

                qwo_40= oc_31 +od_32 +oc_33+od_34 +od_35+od_36            
                qwi_40= ic_31 +id_32 +ic_33+id_34 +id_35+id_36

                sheet.write_merge(c+27, c+28, 1, 13, 'Lưu chuyển tiền thuần từ hoạt động tài chính', style14)
                sheet.write_merge(c+27, c+28, 14, 16, '40', style10)
                sheet.write_merge(c+27, c+28, 17, 19, '', style10)
                sheet.write_merge(c+27, c+28, 20, 23,qwo_40 , style10)
                sheet.write_merge(c+27, c+28, 24, 27, qwi_40, style10)
                
                qwo_50= qwo_20 + qwo_30 +qwo_50
                qwi_50= qwi_20 + qwi_30 +qwi_50

                sheet.write_merge(c+29, c+29, 1, 13, 'Lưu chuyển tiền thuần trong kỳ (50 = 20 + 30 + 40)', style13)
                sheet.write_merge(c+29, c+29, 14, 16, '50', style10)
                sheet.write_merge(c+29, c+29, 17, 19, '', style10)
                sheet.write_merge(c+29, c+29, 20, 23, qwo_50 ,style10)
                sheet.write_merge(c+29, c+29, 24, 27, qwi_50, style10)
                
                sheet.write_merge(c+30, c+30, 1, 13, 'Tiền và tương đường tiền đâu kỳ', style14)
                sheet.write_merge(c+30, c+30, 14, 16, '60', style10)
                sheet.write_merge(c+30, c+30, 17, 19, '', style10)
                sheet.write_merge(c+30, c+30, 20, 23, od_60, style10)
                sheet.write_merge(c+30, c+30, 24, 27, id_60, style10)
                
                sheet.write_merge(c+31, c+31, 1, 13, 'Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ', style13)
                sheet.write_merge(c+31, c+31, 14, 16, '61', style10)
                sheet.write_merge(c+31, c+31, 17, 19, '', style10)
                sheet.write_merge(c+31, c+31, 20, 23, oc_61, style10)
                sheet.write_merge(c+31, c+31, 24, 27, ic_61, style10)
                
                qw0_71= qwo_50 +od_60 +oc_61
                qwi_71= qwi_50 +od_60 +oc_61

                sheet.write_merge(c+32, c+32, 1, 13, 'Tiền và tương đương tiền cuối kỳ (70 = 50 + 60 + 61)', style14)
                sheet.write_merge(c+32, c+32, 14, 16, '71', style10)
                sheet.write_merge(c+32, c+32, 17, 19, 'VIII', style10)
                sheet.write_merge(c+32, c+32, 20, 23, qw0_71, style10)
                sheet.write_merge(c+32, c+32, 24, 27, qwi_71, style10)
                filename = ('%s'+ '.xls') %(self._name)
                workbook.save(r'%s%s' %(path,filename))
                fp = open(r'%s%s' %(path,filename), "rb")
                file_data = fp.read()
                out = base64.encodestring(file_data)                                                 
                            
                # Files actions         
                attach_vals = {
                        'cash_flow_data': self._name + '.xls',
                        'file_name': out,
                    }
                    
                act_id = self.env['account.cash.flows'].create(attach_vals)
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

class CashFlowsView(models.AbstractModel):
    _name='report.smart_invoice.cash_flows_display'

    @api.model
    def _get_report_values(self,docids,data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= end_date + ' 23:59:59'
        filter_date = data['form']['filter_date']
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
            (start_date, start_date, end_date)
        )
        self.cash_flow = self.env.cr.fetchall()

        oc_01 = 0
        ic_01 = 0
        qw_01 = []
        
        od_02= 0
        id_02 = 0
        qw_02= []
        
        od_03 = 0
        id_03 = 0
        qw_03 = []
        
        od_04 = 0
        id_04 = 0
        qw_04 = []
        
        od_05 = 0
        id_05 = 0
        qw_05 = []
        
        oc_06 = 0
        ic_06 = 0
        qw_06 = []

        od_07 = 0
        id_07 = 0
        qw_07 = []
        

        od_21 = 0
        id_21 = 0
        qw_21 = []

        od_22 = 0
        id_22 = 0
        qw_22 = []

        od_23 = 0
        id_23 = 0
        qw_23 = []


        oc_24 = 0
        ic_24 = 0
        qw_24 = []

        od_25 = 0
        id_25 = 0
        qw_25 = []

        oc_26 = 0
        ic_26 = 0
        qw_26 = []

        oc_27 = 0
        ic_27 = 0
        qw_27 = []

        oc_31 = 0
        ic_31 = 0
        qw_31 = []

        od_32 = 0
        id_32 = 0
        qw_32 = []

        oc_33 = 0
        ic_33 = 0
        qw_33 = []       

        od_34 = 0
        id_34 = 0
        qw_34 = []

        od_35 = 0
        id_35 = 0
        qw_35 = []

        od_36 = 0
        id_36 = 0
        qw_36 = []

        od_60 = 0
        id_60=0
        qw_60 = []

        oc_61 = 0
        ic_61 = 0
        qw_61 = []


        isMoney = True
        _time = 2

        for item in self.cash_flow:
            if item[0] == '511':
                oc_01 += item[3]
                ic_01 += item[5]

            if item[0] == '3331':
                oc_01 += item[3]
                ic_01 += item[5]

            if item[0] == '131':
                oc_01 += item[3]
                ic_01 += item[5]

            if item[0] == '1211':
                oc_01 += item[3]
                ic_01 += item[5]

            if item[0] == '1212':
                oc_01 += item[3]
                ic_01 += item[5]

            if item[0] == '1218':
                oc_01 += item[3]
                ic_01 += item[5]

            if item[0] == '331' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '151' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '152' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1531' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1532' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1533' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1534' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '154' :
                od_02 += item[2]
                id_02 += item[4]
                    
            if item[0] == '1551' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1557' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1561' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1562' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '1567' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '157' :
                od_02 += item[2]
                id_02 += item[4]

            if item[0] == '158' :
                od_02 += item[2]
                id_02 += item[4]


            if item[0] == '3341':
                od_03 += item[2]
                id_03 += item[4]

            if item[0] == '3348':
                od_03 += item[2]
                id_03 += item[4]

            if item[0] == '335':
                od_04 += item[2]
                id_04 += item[4]


            if item[0] == '635':
                od_04 += item[2]
                id_04 += item[4]           

            if item[0] == '242':
                od_04 += item[2]
                id_04 += item[4]            

            if item[0] == '3334':
                od_05 += item[2]
                id_05 += item[4]

            if item[0] == '711':
                oc_06 += item[3]
                ic_06 += item[5]


            if item[0] == '1331':
                oc_06 += item[3]
                ic_06 += item[5]

            if item[0] == '1332':
                oc_06 += item[3]
                ic_06 += item[5]

            if item[0] == '141':
                oc_06 += item[3]
                ic_06 += item[5]   

            if item[0] == '244':
                oc_06 += item[3]
                ic_06 += item[5]

            if item[0] == '811':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '1611':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '1612':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '244':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3331':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '33311':
                od_07 += item[2]
                id_07 += item[4]                

            if item[0] == '33312':
                od_07 += item[2]
                id_07 += item[4]                       

            if item[0] == '3332':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3333':
                od_07 += item[2]
                id_07 += item[4]


            if item[0] == '3334':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3335':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3336':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3337':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '33381':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '33382':
                od_07 += item[2]
                id_07 += item[4]


            if item[0] == '3339':
                od_07 += item[2]
                id_07 += item[4]
                
            if item[0] == '3381':
                od_07 += item[2]
                id_07 += item[4]
        

            if item[0] == '3382':
                od_07 += item[2]
                id_07 += item[4]


            if item[0] == '344':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3521':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3522':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3523':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3524':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3531':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3532':
                od_07 += item[2]
                id_07 += item[4]
        
            if item[0] == '3533':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3534':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3561':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '3562':
                od_07 += item[2]
                id_07 += item[4]

            if item[0] == '2111':
                od_21 += item[2]
                id_21 += item[4]

            if item[0] == '2112':
                od_21 += item[2]
                id_21 += item[4]                                                                              
                
            if item[0] == '2113':
                od_21 += item[2]
                id_21 += item[4]

            if item[0] == '2114':
                od_21 += item[2]
                id_21 += item[4]
                                                                                            
            if item[0] == '2115':
                od_21 += item[2]
                id_21 += item[4]

            if item[0] == '2118':
                od_21 += item[2]
                id_21 += item[4]
                
            if item[0] == '2131':
                od_21 += item[2]
                id_21 += item[4]
                
            if item[0] == '2132':
                od_21 += item[2]
                id_21 += item[4]                   
            if item[0] == '2133':
                od_21 += item[2]
                id_21 += item[4]  
            if item[0] == '2134':
                od_21 += item[2]
                id_21 += item[4]  

            if item[0] == '2135':
                od_21 += item[2]
                id_21 += item[4]
                
            if item[0] == '2136':
                od_21 += item[2]
                id_21 += item[4]
                
            if item[0] == '2138':
                od_21 += item[2]
                id_21 += item[4]

            if item[0] == '217':
                od_21 += item[2]
                id_21 += item[4]

            if item[0]=='2411':
                od_21 += item[2]
                id_21 += item[4]

            if item[0]=='2412':
                od_21 += item[2]
                id_21 += item[4]

            if item[0]=='2413':
                od_21 += item[2]
                id_21 += item[4]
            if item[0] == '3411':
                od_21 += item[2]
                id_21 += item[4]

            # 2xx o day
            if item[0] == '632':
                od_22 += item[2]
                id_22 += item[4]
            
            if item[0] == '811':
                od_22 += item[2]
                id_22 += item[4]

            if item[0] == '1281' :
                od_23 += item[2]
                id_23 += item[4]

            if item[0] == '1282' :
                od_23 += item[2]
                id_23 += item[4]

            if item[0] == '1288':
                od_23 += item[2]
                id_23 += item[4]

            if item[0] == '171':
                od_23 += item[2]
                id_23 += item[4]

            if item[0] == '1281' :
                oc_24 += item[3]
                ic_24 += item[5]

            if item[0] == '1282' :
                oc_24 += item[3]
                ic_24 += item[5]

            if item[0] == '1288':
                oc_24 += item[3]
                ic_24 += item[5]

            if item[0] == '171':
                oc_24 += item[3]
                ic_24 += item[5]
            
            if item[0] == '221':
                od_25 += item[2]
                id_25 += item[4]

            if item[0] == '222':
                od_25 += item[2]
                id_25 += item[4]

            if item[0] == '2281':
                od_25 += item[2]
                id_25 += item[4]

            if item[0] == '331':
                od_25 += item[2]
                id_25 += item[4]


            
            if item[0] == '221':
                oc_26 += item[3]
                ic_26 += item[5]

            if item[0] == '222':
                oc_26 += item[3]
                ic_26 += item[5]

            if item[0] == '2281':
                oc_26 += item[3]
                ic_26 += item[5]

            if item[0] == '331':
                oc_26 += item[3]
                ic_26 += item[5]


            if item[0] == '515':
                oc_27 += item[3]
                ic_27 += item[5]

            # end

            if item[0] == '41111':
                oc_31 += item[3]
                ic_31 += item[5]
    
            if item[0] == '41112':
                oc_31 += item[3]
                ic_31 += item[5]    
        
            if item[0] == '4112':
                oc_31 += item[3]
                ic_31 += item[5]            

            if item[0] == '4113':
                oc_31 += item[3]
                ic_31 += item[5]

            if item[0] == '4118':
                oc_31 += item[3]
                ic_31 += item[5]



            if item[0] == '41111':
                od_32 += item[2]
                id_32 += item[4]
    
            if item[0] == '41112':
                od_32 += item[2]
                id_32 += item[4]    
        
            if item[0] == '4112':
                od_32 += item[2]
                id_32 += item[4]            

            if item[0] == '4113':
                od_32 += item[2]
                id_32 += item[4]

            if item[0] == '4118':
                od_32 += item[2]
                id_32 += item[4]

            
            if item[0] == '419':
                od_32 += item[2]
                id_32 += item[4]     

            if item[0] == '3411':
                oc_33 += item[3]
                ic_33 += item[5]     
                

            if item[0] == '3431':
                oc_33 += item[3]
                ic_33 += item[5]     

            if item[0] == '3432':
                oc_33 += item[3]
                ic_33 += item[5]


            if item[0] == '41112':
                oc_33 += item[3]
                ic_33 += item[5]
                
            if item[0] == '3411':
                od_34 += item[2]
                id_34 += item[4]     
                

            if item[0] == '3431':
                od_34 += item[2]
                id_34 += item[4]     

            if item[0] == '3432':
                od_34 += item[2]
                id_34 += item[4]


            if item[0] == '41112':
                od_34 += item[2]
                id_34 += item[4]     



            if item[0] == '3412':
                od_35 += item[2]
                id_35 += item[4]    


            if item[0] == '4211':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '4212':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3381':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3382':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3383':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3384':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3385':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3386':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3387':
                od_36 += item[2]
                id_36 += item[4]

            if item[0] == '3388':
                od_36 += item[2]
                id_36 += item[4]




            if item[0] == '1111':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1112':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1113':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1121':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1122':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1123':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1131':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1132':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1281' :
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '1288':
                od_60 += item[2]
                id_60 += item[4]

            if item[0] == '4131':
                oc_61 += item[3]
                ic_61 += item[5]






        qw_60.append({
            'od_60': od_60,
            'id_60': id_60
        })
        qw_01.append({
            'oc_01': oc_01,
            'ic_01': ic_01
        })
        qw_02.append({
            'od_02': od_02,
            'id_02': id_02
            
        })

        qw_03.append({
            'od_03': od_03,
            'id_03': id_03
            
        })
        qw_04.append({
            'od_04': od_04,
            'id_04' :id_04
        })
        qw_05.append({
            'od_05': od_05,
            'id_05':id_05
        })
        qw_06.append({
            'oc_06': oc_06,
            'ic_06':ic_06
        })
        qw_07.append({
            'od_07': od_07,
            'id_07':id_07
        })
        qw_21.append({
            'od_21': od_21,
            'id_21':id_21
        })

        qw_22.append({
            'od_22':od_22,
            'id_22':id_22
        })
        qw_23.append({
            'od_23':od_23,
            'id_23':id_23
        })
        qw_24.append({
            'oc_24' :oc_24,
            'ic_24' :ic_24
        })
        qw_25.append({
            'od_25':od_25,
            'id_25': id_25
        })
        qw_26.append({
            'oc_26':oc_26,
            'ic_26':ic_26
        })
        qw_27.append({
            'oc_27':oc_27,
            'ic_27'  :ic_27
        })
        qw_31.append({
            'oc_31': oc_31,
            'ic_31' :ic_31
        })
        qw_32.append({
            'od_32': od_32,
            'id_32': id_32
            
        })
        qw_33.append({
            'oc_33':oc_33,
            'ic_33' :ic_33
        })
        qw_34.append({
            'od_34':od_34,
            'id_34':id_34
        })
        qw_35.append({
            'od_35':od_35,
            'id_35':id_35
        })
        qw_36.append({
            'od_36':od_36,
            'id_36':id_36
        })
        qw_61.append({
            'oc_61':oc_61,
            'ic_61':ic_61
        })
        return{
            'doc_ids':data['ids'],
            'doc_model':data['model'],
            'start_date':start_date,
            'end_date': end_date,
            'qw_01': qw_01, 'qw_02': qw_02, 'qw_03': qw_03, 'qw_04': qw_04, 'qw_05': qw_05, 'qw_06': qw_06, 'qw_07': qw_07,
            'qw_21': qw_21, 'qw_22': qw_22, 'qw_23': qw_23, 'qw_24': qw_24, 'qw_25': qw_25, 'qw_26': qw_26, 'qw_27': qw_27,
            'qw_31':qw_31,'qw_32':qw_32,'qw_33':qw_33,'qw_34':qw_34,'qw_35':qw_35,'qw_36':qw_36,
            'qw_60': qw_60,'qw_61': qw_61,
            
        }
             
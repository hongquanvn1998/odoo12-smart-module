from odoo import api,models,fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
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

class AllBalanceSheet(models.TransientModel):
    _name = 'account.all.balance.sheet'
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
    # data_from = fields.Boolean('Lấy dữ liệu từ BCTC đã lập')
    # not_display = fields.Boolean('Không hiển thị các chỉ tiêu có số liệu = 0')
    # accounted = fields.Boolean('BCTC đã được kiểm toán')
       
    def _get_default_company(self):
        company = self.env['res.company'].search([])
        return company
    filter_company = fields.Many2one(string='Company',  comodel_name='res.company')
     
    all_balance_data = fields.Char('Name', size=256)
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
            },
        }
        return self.env.ref('smart_invoice.all_balance_sheet').report_action(self, data=data)


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
                 (select max(credit) from unnest(array[0,COALESCE (opening.credit,0)+COALESCE (incurred.credit,0)- COALESCE (incurred.debit,0) - COALESCE (opening.debit,0)]) credit  )  close_credit 
                 ,incurred.date date
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
                self.all_balance = self.env.cr.fetchall() 
                od_100 = 0
                id_100=0
                
                od_110 = 0
                id_110=0
                
                od_111 = 0
                id_111 = 0

                od_112 = 0
                id_112 = 0
                
                od_120 = 0
                id_120 = 0
                

                od_121 = 0
                id_121 = 0

                od_122 = 0
                id_122 = 0

                od_123 = 0
                id_123 = 0



                od_130 = 0
                id_130 = 0

                od_131 = 0
                id_131 = 0

                od_132 = 0
                id_132 = 0

                od_133 = 0
                id_133 = 0

                od_134 = 0
                id_134 = 0

                od_135 = 0
                id_135 = 0

                od_136 = 0
                id_136 = 0

                oc_137 = 0
                ic_137 = 0

                od_139 = 0
                id_139 = 0

                od_140 = 0
                id_140 = 0

                od_141 = 0
                id_141 = 0

                oc_149 = 0
                ic_149 = 0

                od_150 = 0
                id_150 = 0

                od_151 = 0
                id_151 = 0

                od_152 = 0
                id_152 = 0

                od_153 = 0
                id_153 = 0
                
                od_154 = 0
                id_154 = 0
                
                od_155 = 0
                id_155 = 0
                
                od_200 = 0
                id_200 = 0

                od_210 = 0
                id_210 = 0

                od_211 = 0
                id_211 = 0

                od_212 = 0
                id_212= 0

                od_213 = 0
                id_213 = 0

                od_214 = 0
                id_214= 0

                od_215= 0
                id_215= 0

                od_216= 0
                id_216= 0

                oc_219= 0
                ic_219= 0


                od_200= 0
                id_200= 0


                od_220= 0
                id_220= 0

                od_221= 0
                id_221= 0

                od_222= 0
                id_222= 0

                oc_223= 0
                ic_223= 0

                od_224= 0
                id_224= 0

                od_225= 0
                id_225 = 0

                oc_226= 0
                ic_226= 0
                
                od_227= 0
                id_227= 0

                od_228 =0
                id_228 = 0

                oc_229= 0
                ic_229 =0

                od_230= 0
                id_230= 0

                od_231= 0
                id_231= 0

                oc_232= 0
                ic_232= 0

                od_240= 0
                id_240= 0

                od_241= 0
                id_241= 0

                od_242= 0
                id_242= 0

                od_250= 0
                id_250= 0

                od_251= 0
                id_251= 0

                od_252= 0
                id_252= 0

                od_253= 0
                id_253= 0
                
        
                oc_254= 0
                ic_254= 0
                
        
                od_255= 0
                id_255= 0

                od_260 = 0
                id_260 = 0

                od_261 = 0
                id_261 = 0
                
                od_262 = 0
                id_262 = 0

                od_263 = 0
                id_263 = 0

                od_268 = 0
                id_268 = 0



                od_270 = 0
                id_270 = 0

                oc_300 = 0
                ic_300 = 0
                
                oc_310 = 0
                ic_310 = 0


                oc_330 = 0
                ic_330 = 0

                oc_311 = 0
                ic_311 = 0

                oc_312 = 0
                ic_312 = 0

                oc_313 = 0
                ic_313 = 0

                oc_314 = 0
                ic_314 = 0

                oc_315 = 0
                ic_315 = 0

                oc_316 = 0
                ic_316 = 0

                oc_317 = 0
                ic_317 = 0
                        
                oc_318 = 0
                ic_318= 0
        
                oc_319 = 0
                ic_319 = 0

                oc_320 = 0
                ic_320 = 0
                        
                oc_321 = 0
                ic_321 = 0
                    
                oc_322 = 0
                ic_322 = 0
        
                oc_323 = 0
                ic_323 = 0
                    
            
                oc_324 = 0
                ic_324 = 0
                
                oc_331 = 0
                ic_331 = 0

                oc_332 = 0
                ic_332 = 0
                    
                oc_333 = 0
                ic_333 = 0
                        
                oc_334 = 0
                ic_334 = 0
                        
                oc_335 = 0
                ic_335 = 0

                oc_336 = 0
                ic_336 = 0
                    
                oc_337 = 0
                ic_337 = 0
                                        
                oc_338 = 0
                ic_338 = 0
                        
                oc_339 = 0
                ic_339 = 0
                    
                oc_340 = 0
                ic_340 = 0
                                
                oc_341 = 0
                ic_341 = 0
                    
                oc_342 = 0
                ic_342 = 0
                    
                oc_343 = 0
                ic_343 = 0

                oc_411a = 0
                ic_411a = 0

                oc_411b = 0
                ic_411b = 0

                oc_412 = 0
                ic_412 = 0

                oc_413 = 0
                ic_413 = 0

                oc_414 = 0
                ic_414 = 0
                

                oc_415 = 0
                ic_415 = 0
                
                oc_416 = 0
                ic_416 = 0
                

                oc_417 = 0
                ic_417 = 0

                oc_418 = 0
                ic_418 = 0

                oc_419= 0
                ic_419= 0
                                                                                    

                oc_420 = 0
                ic_420 = 0

        
                oc_421a = 0
                ic_421a = 0

        
                od_421b = 0
                id_421b = 0
                


                oc_422 = 0
                ic_422 = 0


                oc_431 = 0
                ic_431 = 0


                oc_432 = 0
                ic_432 = 0


                oc_440 = 0
                ic_440 = 0

                oc_400 = 0
                ic_400 = 0


                oc_410 = 0
                ic_410 = 0



                oc_411 = 0
                ic_411 = 0


                oc_421 = 0
                ic_421 = 0


                oc_430 = 0
                ic_430 = 0

                _isMoney = True
                

                for item in self.all_balance:
                    x = item[6]
                    _time = relativedelta(self.start_date, x).months

                    if item[0] == '1111':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1112':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1113':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1121':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1122':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1123':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1131':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1132':
                        od_111 += item[2]
                        id_111 += item[4]

                    if item[0] == '1281' and _time <3:
                        od_112 += item[2]
                        id_112 += item[4]

                    if item[0] == '1288' and  _time <3:
                        od_112 += item[2]
                        id_112 += item[4]

                    if item[0] == '1211':
                        od_121 += item[2]
                        id_121 += item[4]

                    if item[0] == '1212':
                        od_121 += item[2]
                        id_121 += item[4]

                    if item[0] == '1218':
                        od_121 += item[2]
                        id_121 += item[4]

                    if item[0] == '2291':
                        od_122 += item[3]
                        id_122 += item[5]

                    if item[0] == '1281' and _isMoney== False and _time <12:
                        od_123 += item[2]
                        id_123 += item[4]

                    if item[0] == '1282' and _isMoney== False and _time <12:
                        od_123 += item[2]
                        id_123 += item[4]

                    if item[0] == '1288' and _isMoney== False and _time <12:
                        od_123 += item[2]
                        id_123 += item[4]

                    if item[0] == '131' and _time <12:
                        od_131 += item[2]
                        id_131 += item[4]


                    if item[0] == '331' and _time<12:
                        od_132 += item[2]
                        id_132 += item[4]

                    if item[0] == '1362' and _time<12:
                        od_133 += item[2]
                        id_133 += item[4]

                    if item[0] == '1363' and _time<12:
                        od_133 += item[2]
                        id_133 += item[4]

                    if item[0] == '1368' and _time<12:
                        od_133 += item[2]
                        id_133 += item[4]

                    if item[0] == '337':
                        od_134 += item[2]
                        id_134 += item[4]

                    if item[0] == '1283' and _time<12:
                        od_135 += item[2]
                        id_135 += item[4]

                    if item[0] == '1385' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]

                    if item[0] == '1388' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]
                        
                    if item[0] == '3341' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]
                                
                    if item[0] == '3348' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]
                                
                    if item[0] == '3381' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]
                                
                    if item[0] == '3388' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]
                                
                    if item[0] == '141' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]

                    if item[0] == '244' and _time<12:
                        od_136 += item[2]
                        id_136 += item[4]

                    if item[0] == '2293':
                        oc_137+= item[3]
                        ic_137 += item[5]
                    
                    if item[0] == '1381':
                        od_139+= item[2]
                        id_139 += item[4]

                    if item[0] == "151":
                        od_141 += item[2]
                        id_141 += item[4]

                    if item[0] == "1531":
                        od_141 += item[2]
                        id_141 += item[4]

                    if item[0] == "1532":
                        od_141 += item[2]
                        id_141 += item[4]

                    if item[0] == "1533":
                        od_141 += item[2]
                        id_141 += item[4]

                    if item[0] == "1534":
                        od_141 += item[2]
                        id_141 += item[4]
                    if item[0] == "1551":
                        od_141 += item[2]
                        id_141 += item[4]

                    if item[0] == "1557":
                        od_141+= item[2]
                        id_141+= item[4]

                    if item[0] == "1561":
                        od_141 += item[2]
                        id_141 += item[4]

                    if item[0] == "1562":
                        od_141 += item[2]
                        id_141 += item[4]

                    if item[0] == "1567":
                        od_141 += item[2]
                        id_141 += item[4]
                    
                    if item[0] == "2294":
                        oc_149 += item[3]
                        ic_149 += item[5]
                    
                    if item[0] == "2421" and _time<12:
                        od_151 += item[2]
                        id_151 += item[4]
                    
                    if item[0] == "1331":
                        od_152 += item[2]
                        id_152 += item[4]

                    if item[0] == "1332":
                        od_152 += item[2]
                        id_152 += item[4]

                    if item[0] == '3331':
                        od_153 += item[2]
                        id_153 += item[4]

                    if item[0] == '33311':
                        od_153 += item[2]
                        id_153 += item[4]                

                    if item[0] == '33312':
                        od_153 += item[2]
                        id_153 += item[4]                        

                    if item[0] == '3332':
                        od_153 += item[2]
                        id_153 += item[4]

                    if item[0] == '3333':
                        od_153 += item[2]
                        id_153 += item[4]


                    if item[0] == '3334':
                        od_153 += item[2]
                        id_153 += item[4]

                    if item[0] == '3335':
                        od_153 += item[2]
                        id_153 += item[4]

                    if item[0] == '3336':
                        od_153 += item[2]
                        id_153 += item[4]

                    if item[0] == '3337':
                        od_153 += item[2]
                        id_153 += item[4]

                    if item[0] == '33381':
                        od_153 += item[2]
                        id_153 += item[4]

                    if item[0] == '33382':
                        od_153 += item[2]
                        id_153 += item[4]


                    if item[0] == '3339':
                        od_153 += item[2]
                        id_153 += item[4]                              
                    
                    if item[0] == '171':
                        od_154 += item[2]
                        id_154 +=item[4]
                        
                    if item[0] == '2288':
                        od_155 += item[2]
                        id_155 += item[4]

                    if item[0] == '131':
                        od_211 += item[2]
                        id_211 += item[4]

                    if item[0] == '331' and _time >12:
                        od_212 += item[2],
                        id_212 += item[4]

                    if item[0] == '1361':
                        od_213 += item[2]
                        id_213 += item[4]

                    if item[0] == '1362' and _time >12:
                        od_214 += item[2]
                        id_214 += item[4]                

                    if item[0] == '1363' and _time >12:
                        od_214 += item[2]
                        id_214 += item[4]      

                    if item[0] == '1368' and _time >12:
                        od_214 += item[2]
                        id_214 += item[4]

                    if item[0] == '1283' and _time >12:
                        od_215 += item[2]
                        id_215 += item[4]

                    if item[0] == '1385':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '1388':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3341':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3348':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3381':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3382':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3383':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3384':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3385':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3386':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3387':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3388':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3341':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '3348':
                        od_216 += item[2]
                        id_216 += item[4]

                    if item[0] == '2293':
                        oc_219 += item[3]
                        ic_219 += item[5]
                    
                    if item[0] == '2111':
                        od_222 += item[2]
                        id_222 += item[4]
                    if item[0] == '2112':
                        od_222 += item[2]
                        id_222 += item[4]                                                                                
                        
                    if item[0] == '2113':
                        od_222 += item[2]
                        id_222 += item[4]

                    if item[0] == '2114':
                        od_222 += item[2]
                        id_222 += item[4]
                                                                                                    
                    if item[0] == '2115':
                        od_222 += item[2]
                        id_222 += item[4]

                    if item[0] == '2118':
                        od_222 += item[2]
                        id_222 += item[4]       

                    if item[0]=='2141':
                        oc_223 += item[3]                                                                   
                        ic_223 += item[5]    

                    if item[0] == '2121' :
                        od_225 += item[2]
                        id_225 += item[4]
                    

                    if item[0] == '2122':
                        od_225 += item[2]
                        id_225 += item[4]           

                    if item[0] == '2142':
                        oc_226 += item[3]
                        ic_226 += item[5]
                                                                                    
                    # if item[0] == '':
                    #     od_228 += item[2]
                    #     id_228 += item[4]                                                                    
                    # if item[0] == '':
                    #     od_228 += item[2]
                    #     id_228 += item[4]                                     
                        
                    if item[0] == '2131':
                        od_228 += item[2]
                        id_228 += item[4]
                        
                    if item[0] == '2132':
                        od_228 += item[2]
                        id_228 += item[4]                     
                    if item[0] == '2133':
                        od_228 += item[2]
                        id_228 += item[4]     
                    if item[0] == '2134':
                        od_228 += item[2]
                        id_228 += item[4]     

                    if item[0] == '2135':
                        od_228 += item[2]
                        id_228 += item[4]
                        
                    if item[0] == '2136':
                        od_228 += item[2]
                        id_228 += item[4]
                        
                    if item[0] == '2138':
                        od_228 += item[2]
                        id_228 += item[4]
                    
                    if item[0] == '2143':
                        oc_229 += item[3]
                        ic_229 += item[5]     
                    
                    if item[0] == '217':
                        od_231 += item[2]
                        id_231 += item[4]

                    if item[0] == '2147':
                        oc_232 += item[3]
                        ic_232 += item[5]

                    if item[0] == '154' and _time > 12:
                        od_241 += item[2]
                        id_241 += item[4]

                    if item[0] == '2294' and _time > 12:
                        od_241 += item[3]
                        id_241 += item[5]
                    
                    if item[0]=='2411' or item[0]=='2412' or item[0]=='2413':
                        od_242 += item[2]
                        id_242 += item[4]

                    if item[0]=='221':
                        od_251 += item[2]
                        id_251 += item[4]

                    if item[0]=='222':
                        od_252 += item[2]
                        id_252 += item[4]

                    if item[0]=='2281':
                        od_253 += item[2]
                        id_253 += item[4]
                                
                    if item[0]=='2292':
                        oc_254 += item[3]
                        ic_254 += item[5]

                    if item[0]=='1281': #and _time >12:
                        od_255 += item[2]
                        id_255 += item[4]

                    if item[0]=='1282': #and _time >12:
                        od_255 += item[2]
                        id_255 += item[4]

                    if item[0]=='1288':# and _time >12:
                        od_255 += item[2]
                        id_255 += item[4]

                    if item[0] == '242' and _time > 12:
                        od_261 += item[2]
                        id_261 += item[4]


                    if item[0] == '243' :
                        od_262 += item[2]
                        id_262 += item[4]

                    if item[0] == '1534' :
                        od_263 += item[2]
                        id_263 += item[4]

                    if item[0] == '2294' :
                        od_263 += item[3]
                        id_263 += item[5]

                    if item[0] == '2288' :
                        od_268 += item[2]
                        id_268 += item[4]
                    
                    if item[0] == '331' and _time <12:
                        oc_311 += item[3]
                        ic_311 += item[5]

                    if item[0] == '131' and _time<12:
                        oc_312 += item[3]
                        ic_312 += item[5]

                    if item[0] == '3331':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '33311':
                        oc_313 += item[3]
                        ic_313 += item[5]          

                    if item[0] == '33312':
                        oc_313 += item[3]
                        ic_313 += item[5]                   

                    if item[0] == '3332':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '3333':
                        oc_313 += item[3]
                        ic_313 += item[5]


                    if item[0] == '3334':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '3335':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '3336':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '3337':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '33381':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '33382':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '3339':
                        oc_313 += item[3]
                        ic_313 += item[5]

                    if item[0] == '3341':
                        oc_314 += item[3]
                        ic_314 += item[5]

                    if item[0] == '3348':
                        oc_314 += item[3]
                        ic_314 += item[5]

                    if item[0] == '335' and _time <12:
                        oc_315 += item[3]
                        ic_315 += item[5]
                                
                    if item[0] == '3361':
                        oc_316 += item[3]
                        ic_316 += item[5]
                        
                    if item[0] == '3363':
                        oc_316 += item[3]
                        ic_316 += item[5]
                        
                    if item[0] == '3368':
                        oc_316 += item[3]
                        ic_316 += item[5]

                    if item[0] == '337':
                        oc_317 += item[3]
                        ic_317 += item[5]

                    if item[0] == '3387' and _time<12:
                        oc_318 += item[3]
                        ic_318 += item[5]

                    if item[0] == '3381':
                        oc_319 += item[3]
                        ic_319 += item[5]
        

                    if item[0] == '3382':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '3383':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '3384':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '3385':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '3386':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '3387':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '3388':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '1381':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '1385':
                        oc_319 += item[3]
                        ic_319 += item[5]
        
                    if item[0] == '1388':
                        oc_319 += item[3]
                        ic_319 += item[5]

                    if item[0] == '3411' and _time <12:
                        oc_320 += item[3]
                        ic_320 += item[5]
        
                    if item[0] == '3412' and _time <12:
                        oc_320 += item[3]
                        ic_320 += item[5]
        
                    if item[0] == '34311' and _time <12:
                        oc_320 += item[3]
                        ic_320 += item[5]

                    if item[0] == '3521':
                        oc_321 += item[3]
                        ic_321 += item[5]

                    if item[0] == '3522':
                        oc_321 += item[3]
                        ic_321 += item[5]
        
                    if item[0] == '3523':
                        oc_321 += item[3]
                        ic_321 += item[5]
        
                    if item[0] == '3524':
                        oc_321 += item[3]
                        ic_321 += item[5]


                    if item[0] == '3531':
                        oc_322 += item[3]
                        ic_322 += item[5]

                    if item[0] == '3532':
                        oc_322 += item[3]
                        ic_322 += item[5]
        
                    if item[0] == '3533':
                        oc_322 += item[3]
                        ic_322 += item[5]
        
                    if item[0] == '3534':
                        oc_322 += item[3]
                        ic_322 += item[5]
                        
                    if item[0] == '357':
                        oc_323 += item[3]
                        ic_323 += item[5]

                    if item[0] == '171':
                        oc_324 += item[3]
                        ic_324 += item[5]


                    if item[0] == '331' and _time >12:
                        oc_331 += item[3]
                        ic_331 += item[5]

                    if item[0] == '131' and _time >12:
                        oc_332 += item[3]
                        ic_332 += item[5]

                    if item[0] == '335':
                        oc_333 += item[3]
                        ic_333 += item[5]

                    if item[0] == '3361':
                        oc_334 += item[3]
                        ic_334 += item[5]

                    if item[0] == '3362' and _time >12:
                        oc_335 += item[3]
                        ic_335 += item[5]

                    if item[0] == '3363' and _time >12:
                        oc_335 += item[3]
                        ic_335 += item[5]

                    if item[0] == '3368' and _time >12:
                        oc_335 += item[3]
                        ic_335 += item[5]

                    if item[0] == '3387' and _time >12:
                        oc_336 += item[3]
                        ic_336 += item[5]

                    if item[0] == '3381' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]                
                    if item[0] == '3382' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]
                    if item[0] == '3383' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]                        
                    if item[0] == '3384' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]
                        
                    if item[0] == '3385' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]

                    if item[0] == '3386' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]
                    if item[0] == '3387' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]

                    if item[0] == '344' and _time >12:
                        oc_337 += item[3]
                        ic_337 += item[5]

                    if item[0] == '3411' and _time >12:
                        oc_338 += item[3]
                        ic_338 += item[5]

                    if item[0] == '3412' and _time >12:
                        oc_338 += item[3]
                        ic_338 += item[5]

                    if item[0] == '34312' and _time >12:
                        oc_338 -= item[2]
                        ic_338 -= item[4]    

                    if item[0] == '34313' and _time >12:
                        oc_338 += item[3]
                        ic_338 += item[5]    


                    if item[0] == '3432':
                        oc_339 += item[3]
                        ic_339 += item[5]    


                    if item[0] == '41112':
                        oc_340 += item[3]
                        ic_340 += item[5]
                        
                    if item[0] == '347':
                        oc_341 += item[3]
                        ic_341 += item[5]

                    if item[0] == '3521':
                        oc_342 += item[3]
                        ic_342 += item[5]

                    if item[0] == '3522':
                        oc_342 += item[3]
                        ic_342 += item[5]

                    if item[0] == '3523':
                        oc_342 += item[3]
                        ic_342 += item[5]

                    if item[0] == '3524':
                        oc_342 += item[3]
                        ic_342 += item[5]

                    if item[0] == '3561':
                        oc_343 += item[3]
                        ic_343 += item[5]

                    if item[0] == '3562':
                        oc_343 += item[3]
                        ic_343 += item[5]

                    if item[0] == '41111':
                        oc_411a += item[3]
                        ic_411a += item[5]
            
                    if item[0] == '41112':
                        oc_411b += item[3]
                        ic_411b += item[5]      
                
                    if item[0] == '4112':
                        oc_412 += item[3]
                        ic_412 += item[5]             

                    if item[0] == '4113':
                        oc_413 += item[3]
                        ic_413 += item[5]

                    if item[0] == '4118':
                        oc_414 += item[3]
                        ic_414 += item[5]
                    

                    if item[0] == '419':
                        oc_415 += item[2]
                        ic_415 += item[4]            


                    if item[0] == '412':
                        oc_416 += item[3]
                        ic_416 += item[5]

                    if item[0] == '4131':
                        oc_417 += item[3]
                        ic_417 += item[5]

                    if item[0] == '4132':
                        oc_417 += item[3]
                        ic_417 += item[5]

                    if item[0] == '414':
                        oc_418 += item[3]
                        ic_418 += item[5]

                    if item[0] == '417':
                        oc_419 += item[3]
                        ic_419 += item[5]

                    if item[0] == '418':
                        oc_420 += item[3]
                        ic_420 += item[5]

                    if item[0] == '4211':
                        oc_421a += item[3]
                        ic_421a += item[5]

                    if item[0] == '4212':
                        od_421b += item[2]
                        id_421b += item[4]

                    if item[0] == '441':
                        oc_422 += item[3]
                        ic_422 += item[5]

                    if item[0] == '4611':
                        oc_431 += item[3]
                        ic_431 += item[5]

                    if item[0] == '4612':
                        oc_431 += item[3]
                        ic_431 += item[5]

                    if item[0] == '1611':
                        oc_431 -= item[2]
                        ic_431 -= item[4]    

                    if item[0] == '1612':
                        oc_431 -= item[2]
                        ic_431 -= item[4]

                    if item[0] == '466':
                        oc_432 += item[3]
                        ic_432 += item[5]

                od_110 = od_111 + od_112
                id_110= id_111 + id_112
           
                od_120 = od_121 + od_122 + od_123
                id_120 = id_121 + id_122 + id_123
            
                od_130=od_131 + od_132 + od_133 + od_134 + od_135 + oc_137 + od_139 
                id_130=id_131 + id_132 + id_133 + id_134 + id_135 + ic_137 + id_139 
               
                od_140 = od_141 + oc_149
                id_140 = id_141 + ic_149
              
                od_150= od_151 + od_152 + od_153 + od_154 +od_155
                id_150= id_151 + id_152 + id_153 + id_154 +id_155

                od_100 = od_110 + od_120 + od_130 + od_140 + od_150
                id_100 = id_110 + id_120 + id_130 + id_140 + id_150
           
                od_210= od_211 + od_212 + od_213 + od_214 + od_215 + od_216 + oc_219
                id_210= id_211 + id_212 + id_213 + id_214 + id_215 + id_216 + ic_219

                od_221= od_222+ oc_223
                id_221= id_222+ ic_223
              
                od_224= od_225 +oc_226
                id_224= id_225 +ic_226
              

                od_227=od_228 + oc_229
                id_227=id_228 + ic_229
              
                od_230 = od_231 + oc_232
                id_230 = id_231 + ic_232
               
                od_240= od_241 +od_242
                id_240= id_241 +id_242
             
                od_250= od_251 + od_252 + od_253 + oc_254 + od_255
                id_250= id_251 + id_252 + id_253 + ic_254 + id_255
              
                od_260= od_261 + od_262 + od_263 + od_268
                id_260= id_261 + id_262 + id_263 + id_268

                od_220= od_221 + od_224 + od_227
                id_220= id_221 + id_224 + id_227
             
                od_200= od_210 + od_220 + od_230 + od_240 + od_250 + od_260
                id_200= id_210 + id_220 + id_230 + id_240 + id_250 + id_260
            
                od_270= od_100 +od_200
                id_270= id_100 +id_200
              
                oc_310= oc_311 + oc_312 + oc_313 + oc_314 + oc_315 + oc_316 + oc_317 + oc_318 + oc_319 + oc_320 + oc_321 + oc_322 + oc_323 + oc_324
                ic_310= ic_311 + ic_312 + ic_313 + ic_314 + ic_315 + ic_316 + ic_317 + ic_318 + ic_319 + ic_320 + ic_321 + ic_322 + ic_323 + ic_324
               
                oc_330= oc_331 + oc_332 + oc_333 + oc_334 + oc_335 + oc_336 + oc_337 + oc_338 + oc_339 + oc_340 + oc_341 + oc_342 + oc_343
                ic_330= ic_331 + ic_332 + ic_333 + ic_334 + ic_335 + ic_336 + ic_337 + ic_338 + ic_339 + ic_340 + ic_341 + ic_342 + ic_343
           
                oc_300 = oc_310 + oc_330
                ic_300 = ic_310 + ic_330
              
                oc_411 =oc_411a + oc_411b
                ic_411 =ic_411a + ic_411b
             
                oc_421= oc_421a +  od_421b
                ic_421 = ic_421a + id_421b
               
                oc_430= oc_431 + oc_432
                ic_430= ic_431 + ic_432
               
                oc_410=oc_411 + oc_412 + oc_413 + oc_414 + oc_415 + oc_416 + oc_417 + oc_418 + oc_419 + oc_420+oc_421 + oc_422
                ic_410=ic_411 + ic_412 + ic_413 + ic_414 + ic_415 + ic_416 + ic_417 + ic_418 + ic_419 + ic_420 + ic_421 + ic_422
             
                oc_400= oc_410 + oc_430
                ic_400= ic_410 + ic_430
            
                oc_440 = oc_300 +oc_400
                ic_440 = ic_300 +ic_400

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
                sheet.write_merge(2, 4, 4, 23, 'BẢNG CÂN ĐỐI KẾ TOÁN', style8)
                sheet.write_merge(5, 6, 4, 23, 'Từ ngày  : %s Đến ngày : %s' %(self.start_date, self.start_date), style12) 
                sheet.write_merge(c, c+1, 1, 13, 'Chỉ tiêu', style0)
                sheet.write_merge(c, c+1, 14, 16, 'Mã số', style0)
                sheet.write_merge(c, c+1, 17, 19, 'Thuyết minh', style0)
                sheet.write_merge(c, c+1, 20, 23, 'Số cuối kỳ', style0)
                sheet.write_merge(c, c+1, 24, 27, 'Số đầu kỳ', style0)
                
                # go
                sheet.write_merge(c+2, c+2, 1, 13, 'A. TÀI SẢN NGẮN HẠN', style14)
                sheet.write_merge(c+2, c+2, 14, 16, '100', style10)
                sheet.write_merge(c+2, c+2, 17, 19, '', style10)
                sheet.write_merge(c+2, c+2, 20, 23, od_100, style10)
                sheet.write_merge(c + 2, c+2, 24, 27, id_100, style10)
                
                sheet.write_merge(c+3, c+3, 1, 13, 'I. Tiền và các khoản tương đương tiền', style14)
                sheet.write_merge(c+3, c+3, 14, 16, '110', style10)
                sheet.write_merge(c+3, c+3, 17, 19, '', style10)
                sheet.write_merge(c+3, c+3, 20, 23,od_110 , style10)
                sheet.write_merge(c + 3, c + 3, 24, 27, id_110, style10)
                
                sheet.write_merge(c+4, c+4, 1, 13, '2. Tiền', style13)
                sheet.write_merge(c+4, c+4, 14, 16, '111', style10)
                sheet.write_merge(c+4, c+4, 17, 19, '', style10)
                sheet.write_merge(c+4, c+4, 20, 23, od_111, style10)
                sheet.write_merge(c+4, c + 4, 24, 27, id_111, style10)
                
                sheet.write_merge(c+5, c+5, 1, 13, '2. Các khoản tương đương tiền', style13)
                sheet.write_merge(c+5, c+5, 14, 16, '112', style10)
                sheet.write_merge(c+5, c+5, 17, 19, '', style10)
                sheet.write_merge(c+5, c+5, 20, 23, od_112, style10)
                sheet.write_merge(c+5, c+5, 24, 27, id_112, style10)
                
                sheet.write_merge(c+6, c+6, 1, 13, 'II. Đầu tư tài chính ngắn hạn', style14)
                sheet.write_merge(c+6, c+6, 14, 16, '120', style10)
                sheet.write_merge(c+6, c+6, 17, 19, '', style10)
                sheet.write_merge(c+6, c+6, 20, 23, od_120, style10)
                sheet.write_merge(c+6, c+6, 24, 27, id_120, style10)
                
                sheet.write_merge(c+7, c+7, 1, 13, '1. Chứng khoán kinh doanh', style13)
                sheet.write_merge(c+7, c+7, 14, 16, '121', style10)
                sheet.write_merge(c+7, c+7, 17, 19, '', style10)
                sheet.write_merge(c+7, c+7, 20, 23, od_121, style10)
                sheet.write_merge(c+7, c+7, 24, 27, id_121, style10)
                
                sheet.write_merge(c+8, c+8, 1, 13, '2. Dự phòng giảm giá chứng khoán kinh doanh(*)', style13)
                sheet.write_merge(c+8, c+8, 14, 16, '122', style10)
                sheet.write_merge(c+8, c+8, 17, 19, '', style10)
                sheet.write_merge(c+8, c+8, 20, 23, od_122, style10)
                sheet.write_merge(c+8, c+8, 24, 27, id_122, style10)
                
                sheet.write_merge(c+9, c+9, 1, 13, '3. Đầu tư nắm giữ đến ngày đáo hạn', style13)
                sheet.write_merge(c+9, c+9, 14, 16, '123', style10)
                sheet.write_merge(c+9, c+9, 17, 19, '', style10)
                sheet.write_merge(c+9, c+9, 20, 23, od_123, style10)
                sheet.write_merge(c+9, c+9, 24, 27, id_123, style10)
                
                sheet.write_merge(c+10, c+10, 1, 13, 'III. Các khoản phải thu ngắn hạn', style14)
                sheet.write_merge(c+10, c+10, 14, 16, '130', style10)
                sheet.write_merge(c+10, c+10, 17, 19, '', style10)
                sheet.write_merge(c+10, c+10, 20, 23, od_130, style10)
                sheet.write_merge(c+10, c+10, 24, 27, id_130, style10)
                
                sheet.write_merge(c+11, c+11, 1, 13, '1. Phải thu ngắn hạn của khách hàng', style13)
                sheet.write_merge(c+11, c+11, 14, 16, '131', style10)
                sheet.write_merge(c+11, c+11, 17, 19, '', style10)
                sheet.write_merge(c+11, c+11, 20, 23, od_131, style10)
                sheet.write_merge(c+11, c+11, 24, 27,id_131 , style10)
                
                sheet.write_merge(c+12, c+12, 1, 13, '2. Trả trước cho người bán ngắn hạn', style13)
                sheet.write_merge(c+12, c+12, 14, 16, '132', style10)
                sheet.write_merge(c+12, c+12, 17, 19, '', style10)
                sheet.write_merge(c+12, c+12, 20, 23, od_132, style10)
                sheet.write_merge(c+12, c+12, 24, 27, id_132, style10)

                sheet.write_merge(c+13, c+13, 1, 13, '3. Phải thu nội bộ ngắn hạn', style13)
                sheet.write_merge(c+13, c+13, 14, 16, '133', style10)
                sheet.write_merge(c+13, c+13, 17, 19, '', style10)
                sheet.write_merge(c+13, c+13, 20, 23, od_133, style10)
                sheet.write_merge(c+13, c+13, 24, 27, id_133, style10)

                sheet.write_merge(c+14, c+14, 1, 13, '4. Phải thu theo tiến độ kế hoạch hợp đồng xây dựng	', style13)
                sheet.write_merge(c+14, c+14, 14, 16, '134', style10)
                sheet.write_merge(c+14, c+14, 17, 19, '', style10)
                sheet.write_merge(c+14, c+14, 20, 23,od_134 , style10)
                sheet.write_merge(c+14, c+14, 24, 27, id_134, style10)

                sheet.write_merge(c+15, c+15, 1, 13, '5. Phải thu về cho vay ngắn hạn', style13)
                sheet.write_merge(c+15, c+15, 14, 16, '135', style10)
                sheet.write_merge(c+15, c+15, 17, 19, '', style10)
                sheet.write_merge(c+15, c+15, 20, 23, od_135, style10)
                sheet.write_merge(c+15, c+15, 24, 27, id_135, style10)

                sheet.write_merge(c+16, c+16, 1, 13, '6. Phải thu ngắn hạn khác', style13)
                sheet.write_merge(c+16, c+16, 14, 16, '136', style10)
                sheet.write_merge(c+16, c+16, 17, 19, '', style10)
                sheet.write_merge(c+16, c+16, 20, 23,od_136 , style10)
                sheet.write_merge(c+16, c+16, 24, 27,id_136 , style10)

                sheet.write_merge(c+17, c+17, 1, 13, '7. Dự phòng phải thu ngắn hạn khó đòi (*)', style13)
                sheet.write_merge(c+17, c+17, 14, 16, '137', style10)
                sheet.write_merge(c+17, c+17, 17, 19, '', style10)
                sheet.write_merge(c+17, c+17, 20, 23, oc_137, style10)
                sheet.write_merge(c+17, c+17, 24, 27, ic_137, style10)

                sheet.write_merge(c+18, c+18, 1, 13, '8. Tài sản thiếu chờ xử lý', style13)
                sheet.write_merge(c+18, c+18, 14, 16, '139', style10)
                sheet.write_merge(c+18, c+18, 17, 19, '', style10)
                sheet.write_merge(c+18, c+18, 20, 23,od_139 , style10)
                sheet.write_merge(c+18, c+18, 24, 27, id_139, style10)
                
                sheet.write_merge(c+19, c+19, 1, 13, 'IV. Hàng tồn kho', style14)
                sheet.write_merge(c+19, c+19, 14, 16, '140', style10)
                sheet.write_merge(c+19, c+19, 17, 19, '', style10)
                sheet.write_merge(c+19, c+19, 20, 23, od_140, style10)
                sheet.write_merge(c+19, c+19, 24, 27,id_140 , style10)
                
                sheet.write_merge(c+20, c+20, 1, 13, '1. Hàng tồn kho', style13)
                sheet.write_merge(c+20, c+20, 14, 16, '141', style10)
                sheet.write_merge(c+20, c+20, 17, 19, '', style10)
                sheet.write_merge(c+20, c+20, 20, 23, od_141, style10)
                sheet.write_merge(c+20, c+20, 24, 27,id_141 , style10)

                
                sheet.write_merge(c+21, c+21, 1, 13, '2.Dự phòng giảm giá hàng tồn kho (*)', style13)
                sheet.write_merge(c+21, c+21, 14, 16, '149', style10)
                sheet.write_merge(c+21, c+21, 17, 19, '', style10)
                sheet.write_merge(c+21, c+21, 20, 23, oc_149, style10)
                sheet.write_merge(c+21, c+21, 24, 27, ic_149, style10)
                
                sheet.write_merge(c+22, c+22, 1, 13, 'V. Tài sản ngắn hạn khác', style14)
                sheet.write_merge(c+22, c+22, 14, 16, '150', style10)
                sheet.write_merge(c+22, c+22, 17, 19, '', style10)
                sheet.write_merge(c+22, c+22, 20, 23, od_150, style10)
                sheet.write_merge(c+22, c+22, 24, 27, id_150, style10)
                
                sheet.write_merge(c+23, c+23, 1, 13, '1. Chi phí trả trước ngắn hạn', style13)
                sheet.write_merge(c+23, c+23, 14, 16, '151', style10)
                sheet.write_merge(c+23, c+23, 17, 19, '', style10)
                sheet.write_merge(c+23, c+23, 20, 23, od_151, style10)
                sheet.write_merge(c+23, c+23, 24, 27, id_151, style10)
                
                sheet.write_merge(c+24, c+24, 1, 13, '2. Thuế GTGT được khấu trừ', style13)
                sheet.write_merge(c+24, c+24, 14, 16, '152', style10)
                sheet.write_merge(c+24, c+24, 17, 19, '', style10)
                sheet.write_merge(c+24, c+24, 20, 23,od_152,style10)
                sheet.write_merge(c+24, c+24, 24, 27,id_152, style10)

                sheet.write_merge(c+25, c+25, 1, 13, '3. Thuế và các khoản khác phải thu Nhà nước', style13)
                sheet.write_merge(c+25, c+25, 14, 16, '153', style10)
                sheet.write_merge(c+25, c+25, 17, 19, '', style10)
                sheet.write_merge(c+25, c+25, 20, 23,od_153 , style10)
                sheet.write_merge(c+25, c+25, 24, 27,id_153 , style10)
                
                sheet.write_merge(c+26, c+26, 1, 13, '4. Giao dịch mua bán lại trái phiếu Chính phủ', style13)
                sheet.write_merge(c+26, c+26, 14, 16, '154', style10)
                sheet.write_merge(c+26, c+26, 17, 19, '', style10)
                sheet.write_merge(c+26, c+26, 20, 23,od_154 , style10)
                sheet.write_merge(c+26, c+26, 24, 27, id_154, style10)
                
                sheet.write_merge(c+27, c+27, 1, 13, '5. Tài sản ngắn hạn khác', style13)
                sheet.write_merge(c+27, c+27, 14, 16, '155', style10)
                sheet.write_merge(c+27, c+27, 17, 19, '', style10)
                sheet.write_merge(c+27, c+27, 20, 23, od_155, style10)
                sheet.write_merge(c+27, c+27, 24, 27,id_155 , style10)
                             
                sheet.write_merge(c+28, c+28, 1, 13, 'B. TÀI SẢN DÀI HẠN', style14)
                sheet.write_merge(c+28, c+28, 14, 16, '200', style10)
                sheet.write_merge(c+28, c+28, 17, 19, '', style10)
                sheet.write_merge(c+28, c+28, 20, 23, od_200, style10)
                sheet.write_merge(c+28, c+28, 24, 27,id_200 , style10)
                
                sheet.write_merge(c+29, c+29, 1, 13, 'I. Các khoản phải thu dài hạn', style14)
                sheet.write_merge(c+29, c+29, 14, 16, '210', style10)
                sheet.write_merge(c+29, c+29, 17, 19, '', style10)
                sheet.write_merge(c+29, c+29, 20, 23, od_210, style10)
                sheet.write_merge(c+29, c+29, 24, 27, id_210, style10)
                
                sheet.write_merge(c+30, c+30, 1, 13, '1. Phải thu dài hạn của khác hàng', style13)
                sheet.write_merge(c+30, c+30, 14, 16, '211', style10)
                sheet.write_merge(c+30, c+30, 17, 19, '', style10)
                sheet.write_merge(c+30, c+30, 20, 23, od_211, style10)
                sheet.write_merge(c+30, c+30, 24, 27,id_211, style10)
                
                sheet.write_merge(c+31, c+31, 1, 13, '2. Trả trước cho người bán dài hạn', style13)
                sheet.write_merge(c+31, c+31, 14, 16, '212', style10)
                sheet.write_merge(c+31, c+31, 17, 19, '', style10)
                sheet.write_merge(c+31, c+31, 20, 23,od_212 , style10)
                sheet.write_merge(c+31, c+31, 24, 27,id_212 , style10)
                
                sheet.write_merge(c+32, c+32, 1, 13, '3. Vốn kinh doanh ở đơn vị trực thuộc', style13)
                sheet.write_merge(c+32, c+32, 14, 16, '213', style10)
                sheet.write_merge(c+32, c+32, 17, 19, '', style10)
                sheet.write_merge(c+32, c+32, 20, 23,od_213 , style10)
                sheet.write_merge(c+32, c+32, 24, 27,id_213 , style10)
               
                sheet.write_merge(c+33, c+33, 1, 13, '4. Phải thu nội bộ dài hạn', style13)
                sheet.write_merge(c+33, c+33, 14, 16, '214', style10)
                sheet.write_merge(c+33, c+33, 17, 19, '', style10)
                sheet.write_merge(c+33, c+33, 20, 23,od_214 , style10)
                sheet.write_merge(c+33, c+33, 24, 27,id_214 , style10)
                
                sheet.write_merge(c+34, c+34, 1, 13, '5. Phải thu về cho vay dài hạn', style13)
                sheet.write_merge(c+34, c+34, 14, 16, '215', style10)
                sheet.write_merge(c+34, c+34, 17, 19, '', style10)
                sheet.write_merge(c+34, c+34, 20, 23,od_215 , style10)
                sheet.write_merge(c+34, c+34, 24, 27, id_215, style10)
                
                sheet.write_merge(c+35, c+35, 1, 13, '6. Phải thu dài hạn khác', style13)
                sheet.write_merge(c+35, c+35, 14, 16, '216', style10)
                sheet.write_merge(c+35, c+35, 17, 19, '', style10)
                sheet.write_merge(c+35, c+35, 20, 23, od_216, style10)
                sheet.write_merge(c+35, c+35, 24, 27, id_216, style10)
                
                sheet.write_merge(c+36, c+36, 1, 13, '7. Dự phòng phải thu dài hạn khó đòi (*)', style13)
                sheet.write_merge(c+36, c+36, 14, 16, '219', style10)
                sheet.write_merge(c+36, c+36, 17, 19, '', style10)
                sheet.write_merge(c+36, c+36, 20, 23,oc_219 , style10)
                sheet.write_merge(c+36, c+36, 24, 27,ic_219 , style10)

                sheet.write_merge(c+37, c+37, 1, 13, 'II. Tài sản cố định', style14)
                sheet.write_merge(c+37, c+37, 14, 16, '220', style10)
                sheet.write_merge(c+37, c+37, 17, 19, '', style10)
                sheet.write_merge(c+37, c+37, 20, 23, od_220, style10)
                sheet.write_merge(c+37, c+37, 24, 27, id_220, style10)
                
                sheet.write_merge(c+38, c+38, 1, 13, '1. Tài sản cố định hữu hình', style13)
                sheet.write_merge(c+38, c+38, 14, 16, '221', style10)
                sheet.write_merge(c+38, c+38, 17, 19, '', style10)
                sheet.write_merge(c+38, c+38, 20, 23, od_221, style10)
                sheet.write_merge(c+38, c+38, 24, 27, id_221, style10)
                
                sheet.write_merge(c+39, c+39, 1, 13, '- Nguyên giá', style13)
                sheet.write_merge(c+39, c+39, 14, 16, '222', style10)
                sheet.write_merge(c+39, c+39, 17, 19, '', style10)
                sheet.write_merge(c+39, c+39, 20, 23, od_222, style10)
                sheet.write_merge(c+39, c+39, 24, 27, id_222, style10)
                
                sheet.write_merge(c+40, c+40, 1, 13, '- Giá trị hao mòn lũy kế (*)', style13)
                sheet.write_merge(c+40, c+40, 14, 16, '223', style10)
                sheet.write_merge(c+40, c+40, 17, 19, '', style10)
                sheet.write_merge(c+40, c+40, 20, 23,oc_223 , style10)
                sheet.write_merge(c+40, c+40, 24, 27, ic_223, style10)

 
                sheet.write_merge(c+41, c+41, 1, 13, '2. Tài sản cố định thuê tài chính', style13)
                sheet.write_merge(c+41, c+41, 14, 16, '224', style10)
                sheet.write_merge(c+41, c+41, 17, 19, '', style10)
                sheet.write_merge(c+41, c+41, 20, 23, od_224, style10)
                sheet.write_merge(c+41, c+41, 24, 27,id_224 , style10)
                
                sheet.write_merge(c+42, c+42, 1, 13, '- Nguyên giá', style13)
                sheet.write_merge(c+42, c+42, 14, 16, '225', style10)
                sheet.write_merge(c+42, c+42, 17, 19, '', style10)
                sheet.write_merge(c+42, c+42, 20, 23, od_225, style10)
                sheet.write_merge(c+42, c+42, 24, 27, id_225, style10)
            
                sheet.write_merge(c+43, c+43, 1, 13, '- Giá trị hao mòn lũy kế (*)', style13)
                sheet.write_merge(c+43, c+43, 14, 16, '226', style10)
                sheet.write_merge(c+43, c+43, 17, 19, '', style10)
                sheet.write_merge(c+43, c+43, 20, 23, oc_226, style10)
                sheet.write_merge(c+43, c+43, 24, 27, ic_226, style10)
                
                sheet.write_merge(c+44, c+44, 1, 13, '3. Tài sản cố định vô hình', style13)
                sheet.write_merge(c+44, c+44, 14, 16, '227', style10)
                sheet.write_merge(c+44, c+44, 17, 19, '', style10)
                sheet.write_merge(c+44, c+44, 20, 23,od_227 , style10)
                sheet.write_merge(c+44, c+44, 24, 27, id_227, style10)     
                    
                sheet.write_merge(c+45, c+45, 1, 13, '- Nguyên giá', style13)
                sheet.write_merge(c+45, c+45, 14, 16, '228', style10)
                sheet.write_merge(c+45, c+45, 17, 19, '', style10)
                sheet.write_merge(c+45, c+45, 20, 23, od_228, style10)
                sheet.write_merge(c+45, c+45, 24, 27, id_228, style10)
                
                sheet.write_merge(c+46, c+46, 1, 13, '- Giá trị hao mòn lũy kế (*)', style13)
                sheet.write_merge(c+46, c+46, 14, 16, '229', style10)
                sheet.write_merge(c+46, c+46, 17, 19, '', style10)
                sheet.write_merge(c+46, c+46, 20, 23,oc_229 , style10)
                sheet.write_merge(c+46, c+46, 24, 27, ic_229, style10)                          
                
                sheet.write_merge(c+47, c+47, 1, 13, 'III. Bất động sản đầu tư', style14)
                sheet.write_merge(c+47, c+47, 14, 16, '230', style10)
                sheet.write_merge(c+47, c+47, 17, 19, '', style10)
                sheet.write_merge(c+47, c+47, 20, 23, od_230, style10)
                sheet.write_merge(c+47, c+47, 24, 27, id_230, style10)     
                    
                sheet.write_merge(c+48, c+48, 1, 13, '- Nguyên giá', style13)
                sheet.write_merge(c+48, c+48, 14, 16, '231', style10)
                sheet.write_merge(c+48, c+48, 17, 19, '', style10)
                sheet.write_merge(c+48, c+48, 20, 23,od_231 , style10)
                sheet.write_merge(c+48, c+48, 24, 27,id_231 , style10)
                
                sheet.write_merge(c+49, c+49, 1, 13, '- Giá trị hao mòn lũy kế (*)', style13)
                sheet.write_merge(c+49, c+49, 14, 16, '232', style10)
                sheet.write_merge(c+49, c+49, 17, 19, '', style10)
                sheet.write_merge(c+49, c+49, 20, 23,oc_232 , style10)
                sheet.write_merge(c+49, c+49, 24, 27, ic_232, style10)                
                
                sheet.write_merge(c+50, c+50, 1, 13, 'IV. Tài sản dở dang dài hạn', style14)
                sheet.write_merge(c+50, c+50, 14, 16, '240', style10)
                sheet.write_merge(c+50, c+50, 17, 19, '', style10)
                sheet.write_merge(c+50, c+50, 20, 23, od_240, style10)
                sheet.write_merge(c+50, c+50, 24, 27,id_240 , style10)     
                    
                sheet.write_merge(c+51, c+51, 1, 13, '1. Chi phí sản xuất, kinh doanh dở dang dài hạn	', style13)
                sheet.write_merge(c+51, c+51, 14, 16, '241', style10)
                sheet.write_merge(c+51, c+51, 17, 19, '', style10)
                sheet.write_merge(c+51, c+51, 20, 23, od_241, style10)
                sheet.write_merge(c+51, c+51, 24, 27, id_241, style10)
                
                sheet.write_merge(c+52, c+52, 1, 13, '2. Chi phí xây dựng cơ bản dở dang', style13)
                sheet.write_merge(c+52, c+52, 14, 16, '242', style10)
                sheet.write_merge(c+52, c+52, 17, 19, '', style10)
                sheet.write_merge(c+52, c+52, 20, 23, od_242, style10)
                sheet.write_merge(c+52, c+52, 24, 27,id_242 , style10)                
              
                sheet.write_merge(c+53, c+53, 1, 13, 'V. Đầu tư tài chính dài hạn', style14)
                sheet.write_merge(c+53, c+53, 14, 16, '250', style10)
                sheet.write_merge(c+53, c+53, 17, 19, '', style10)
                sheet.write_merge(c+53, c+53, 20, 23,od_250 , style10)
                sheet.write_merge(c+53, c+53, 24, 27, id_250, style10)     
                    
                sheet.write_merge(c+54, c+54, 1, 13, '1. Đầu tư vào công ty con', style13)
                sheet.write_merge(c+54, c+54, 14, 16, '251', style10)
                sheet.write_merge(c+54, c+54, 17, 19, '', style10)
                sheet.write_merge(c+54, c+54, 20, 23,od_251 , style10)
                sheet.write_merge(c+54, c+54, 24, 27,id_251, style10)
                
                sheet.write_merge(c+55, c+55, 1, 13, '2. Đầu tư vào công ty liên doanh,liên kết', style13)
                sheet.write_merge(c+55, c+55, 14, 16, '252', style10)
                sheet.write_merge(c+55, c+55, 17, 19, '', style10)
                sheet.write_merge(c+55, c+55, 20, 23, od_252, style10)
                sheet.write_merge(c+55, c+55, 24, 27, id_252, style10)                
                
                sheet.write_merge(c+56, c+56, 1, 13, '3. Đầu tư góp vốn vào đơn vị khác', style13)
                sheet.write_merge(c+56, c+56, 14, 16, '253', style10)
                sheet.write_merge(c+56, c+56, 17, 19, '', style10)
                sheet.write_merge(c+56, c+56, 20, 23, od_253, style10)
                sheet.write_merge(c+56, c+56, 24, 27, id_253, style10)     
                    
                sheet.write_merge(c+57, c+57, 1, 13, '4. Dự phòng đầu tư tài chính dài hạn (*)', style13)
                sheet.write_merge(c+57, c+57, 14, 16, '254', style10)
                sheet.write_merge(c+57, c+57, 17, 19, '', style10)
                sheet.write_merge(c+57, c+57, 20, 23, oc_254, style10)
                sheet.write_merge(c+57, c+57, 24, 27, ic_254, style10)
                
                sheet.write_merge(c+58, c+58, 1, 13, '5. Đầu tư nắm giữ đến ngày đáo hạn', style13)
                sheet.write_merge(c+58, c+58, 14, 16, '255', style10)
                sheet.write_merge(c+58, c+58, 17, 19, '', style10)
                sheet.write_merge(c+58, c+58, 20, 23,od_255 , style10)
                sheet.write_merge(c+58, c+58, 24, 27, id_255, style10)                     

                sheet.write_merge(c+59, c+59, 1, 13, 'VI. Tài sản dài hạn khác', style14)
                sheet.write_merge(c+59, c+59, 14, 16, '260', style10)
                sheet.write_merge(c+59, c+59, 17, 19, '', style10)
                sheet.write_merge(c+59, c+59, 20, 23,od_260 , style10)
                sheet.write_merge(c+59, c+59, 24, 27, id_260, style10)     
                    
                sheet.write_merge(c+60, c+60, 1, 13, '1. Chi phí trả trước dài hạn', style13)
                sheet.write_merge(c+60, c+60, 14, 16, '261', style10)
                sheet.write_merge(c+60, c+60, 17, 19, '', style10)
                sheet.write_merge(c+60, c+60, 20, 23,od_261 , style10)
                sheet.write_merge(c+60, c+60, 24, 27,id_261 , style10)
                
                sheet.write_merge(c+61, c+61, 1, 13, '2. Tài sản thuế thu nhập hoãn lại', style13)
                sheet.write_merge(c+61, c+61, 14, 16, '262', style10)
                sheet.write_merge(c+61, c+61, 17, 19, '', style10)
                sheet.write_merge(c+61, c+61, 20, 23, od_262, style10)
                sheet.write_merge(c+61, c+61, 24, 27, id_262, style10)                
                
                sheet.write_merge(c+62, c+62, 1, 13, '3. Thiết bị, vật tư,phụ tùng thay thế dài hạn', style13)
                sheet.write_merge(c+62, c+62, 14, 16, '263', style10)
                sheet.write_merge(c+62, c+62, 17, 19, '', style10)
                sheet.write_merge(c+62, c+62, 20, 23,od_263 , style10)
                sheet.write_merge(c+62, c+62, 24, 27,id_263 , style10)     
                    
                sheet.write_merge(c+63, c+63, 1, 13, '4. Tài sản dài hạn khác', style13)
                sheet.write_merge(c+63, c+63, 14, 16, '268', style10)
                sheet.write_merge(c+63, c+63, 17, 19, '', style10)
                sheet.write_merge(c+63, c+63, 20, 23, od_268, style10)
                sheet.write_merge(c+63, c+63, 24, 27, id_268, style10)
                
                sheet.write_merge(c+64, c+64, 1, 13, 'TỔNG CỘNG TÀI SẢN (270 = 100 + 200)', style14)
                sheet.write_merge(c+64, c+64, 14, 16, '270', style10)
                sheet.write_merge(c+64, c+64, 17, 19, '', style10)
                sheet.write_merge(c+64, c+64, 20, 23,od_270 , style10)
                sheet.write_merge(c+64, c+64, 24, 27,id_270 , style10)     
                    
                sheet.write_merge(c+65, c+65, 1, 13, 'NGUỒN VỐN', style14)
                sheet.write_merge(c+65, c+65, 14, 16, '', style10)
                sheet.write_merge(c+65, c+65, 17, 19, '', style10)
                sheet.write_merge(c+65, c+65, 20, 23, '', style10)
                sheet.write_merge(c+65, c+65, 24, 27, '', style10)
                
                sheet.write_merge(c+66, c+66, 1, 13, 'C - NỢ PHẢI TRẢ', style14)
                sheet.write_merge(c+66, c+66, 14, 16, '300', style10)
                sheet.write_merge(c+66, c+66, 17, 19, '', style10)
                sheet.write_merge(c+66, c+66, 20, 23,oc_300 , style10)
                sheet.write_merge(c+66, c+66, 24, 27, ic_300, style10)     
                    
                sheet.write_merge(c+67, c+67, 1, 13, 'I. Nợ ngắn hạn', style14)
                sheet.write_merge(c+67, c+67, 14, 16, '310', style10)
                sheet.write_merge(c+67, c+67, 17, 19, '', style10)
                sheet.write_merge(c+67, c+67, 20, 23, oc_310, style10)
                sheet.write_merge(c+67, c+67, 24, 27, ic_310, style10)
                   
                sheet.write_merge(c+68, c+68, 1, 13, '1. Phải trả người bán ngắn hạn', style13)
                sheet.write_merge(c+68, c+68, 14, 16, '311', style10)
                sheet.write_merge(c+68, c+68, 17, 19, '', style10)
                sheet.write_merge(c+68, c+68, 20, 23, oc_311, style10)
                sheet.write_merge(c+68, c+68, 24, 27,ic_311 , style10)     
                    
                sheet.write_merge(c+69, c+69, 1, 13, '2. Người mua trả tiền trước ngắn hạn', style13)
                sheet.write_merge(c+69, c+69, 14, 16, '312', style10)
                sheet.write_merge(c+69, c+69, 17, 19, '', style10)
                sheet.write_merge(c+69, c+69, 20, 23, oc_312, style10)
                sheet.write_merge(c+69, c+69, 24, 27, ic_312, style10)
                
                sheet.write_merge(c+70, c+70, 1, 13, '3. Thuế và các khoản phải nộp Nhà nước', style13)
                sheet.write_merge(c+70, c+70, 14, 16, '313', style10)
                sheet.write_merge(c+70, c+70, 17, 19, '', style10)
                sheet.write_merge(c+70, c+70, 20, 23, oc_313, style10)
                sheet.write_merge(c+70, c+70, 24, 27,ic_313 , style10)                
                
                sheet.write_merge(c+71, c+71, 1, 13, '4. Phải trả người lao động', style13)
                sheet.write_merge(c+71, c+71, 14, 16, '314', style10)
                sheet.write_merge(c+71, c+71, 17, 19, '', style10)
                sheet.write_merge(c+71, c+71, 20, 23,oc_314 , style10)
                sheet.write_merge(c+71, c+71, 24, 27,ic_314 , style10)     
                    
                sheet.write_merge(c+72, c+72, 1, 13, '5. Chi phí phải trả ngắn hạn', style13)
                sheet.write_merge(c+72, c+72, 14, 16, '315', style10)
                sheet.write_merge(c+72, c+72, 17, 19, '', style10)
                sheet.write_merge(c+72, c+72, 20, 23,oc_315 , style10)
                sheet.write_merge(c+72, c+72, 24, 27, ic_315, style10)
                                  
                sheet.write_merge(c+73, c+73, 1, 13, '6. Phải trả nội bộ ngắn hạn', style13)
                sheet.write_merge(c+73, c+73, 14, 16, '316', style10)
                sheet.write_merge(c+73, c+73, 17, 19, '', style10)
                sheet.write_merge(c+73, c+73, 20, 23,oc_316 , style10)
                sheet.write_merge(c+73, c+73, 24, 27, ic_316, style10)     
                    
                sheet.write_merge(c+74, c+74, 1, 13, '7. Phải trả theo tiến độ kế hoạch hợp đồng xây dựng', style13)
                sheet.write_merge(c+74, c+74, 14, 16, '317', style10)
                sheet.write_merge(c+74, c+74, 17, 19, '', style10)
                sheet.write_merge(c+74, c+74, 20, 23, oc_317, style10)
                sheet.write_merge(c+74, c+74, 24, 27,ic_317 , style10)
                
                sheet.write_merge(c+75, c+75, 1, 13, '8. Doanh thu chưa thực hiện ngắn hạn', style13)
                sheet.write_merge(c+75, c+75, 14, 16, '318', style10)
                sheet.write_merge(c+75, c+75, 17, 19, '', style10)
                sheet.write_merge(c+75, c+75, 20, 23, oc_318, style10)
                sheet.write_merge(c+75, c+75, 24, 27, ic_318, style10)                
                
                sheet.write_merge(c+76, c+76, 1, 13, '9. Phải trả ngắn hạn khác', style13)
                sheet.write_merge(c+76, c+76, 14, 16, '319', style10)
                sheet.write_merge(c+76, c+76, 17, 19, '', style10)
                sheet.write_merge(c+76, c+76, 20, 23, oc_319, style10)
                sheet.write_merge(c+76, c+76, 24, 27,ic_319 , style10)     
                    
                sheet.write_merge(c+77, c+77, 1, 13, '10. Vay và nợ thuê tài chính ngắn hạn', style13)
                sheet.write_merge(c+77, c+77, 14, 16, '320', style10)
                sheet.write_merge(c+77, c+77, 17, 19, '', style10)
                sheet.write_merge(c+77, c+77, 20, 23, oc_320, style10)
                sheet.write_merge(c+77, c+77, 24, 27,ic_320 , style10)

                sheet.write_merge(c+78, c+78, 1, 13, '11. Dự phòng phải trả ngắn hạn', style13)
                sheet.write_merge(c+78, c+78, 14, 16, '321', style10)
                sheet.write_merge(c+78, c+78, 17, 19, '', style10)
                sheet.write_merge(c+78, c+78, 20, 23,oc_321 , style10)
                sheet.write_merge(c+78, c+78, 24, 27, ic_321, style10)
                
                sheet.write_merge(c+79, c+79, 1, 13, '12. Quỹ khen thưởng. phúc lợ', style13)
                sheet.write_merge(c+79, c+79, 14, 16, '322', style10)
                sheet.write_merge(c+79, c+79, 17, 19, '', style10)
                sheet.write_merge(c+79, c+79, 20, 23,oc_322 , style10)
                sheet.write_merge(c+79, c+79, 24, 27,ic_322 , style10)                
                
                sheet.write_merge(c+80, c+80, 1, 13, '13. Quỹ bình ổn giá', style13)
                sheet.write_merge(c+80, c+80, 14, 16, '323', style10)
                sheet.write_merge(c+80, c+80, 17, 19, '', style10)
                sheet.write_merge(c+80, c+80, 20, 23,oc_323 , style10)
                sheet.write_merge(c+80, c+80, 24, 27,ic_323 , style10)     
                    
                sheet.write_merge(c+81, c+81, 1, 13, '14. Giao dịch mua bán lại trái phiến Chính phủ', style13)
                sheet.write_merge(c+81, c+81, 14, 16, '324', style10)
                sheet.write_merge(c+81, c+81, 17, 19, '', style10)
                sheet.write_merge(c+81, c+81, 20, 23,oc_324 , style10)
                sheet.write_merge(c+81, c+81, 24, 27,ic_324 , style10)

                sheet.write_merge(c+82, c+82, 1, 13, 'II. Nợ dài hạn', style14)
                sheet.write_merge(c+82, c+82, 14, 16, '330', style10)
                sheet.write_merge(c+82, c+82, 17, 19, '', style10)
                sheet.write_merge(c+82, c+82, 20, 23, oc_330, style10)
                sheet.write_merge(c+82, c+82, 24, 27,ic_330 , style10)
                   
                sheet.write_merge(c+83, c+83, 1, 13, '1. Phải trả dài hạn người bán', style13)
                sheet.write_merge(c+83, c+83, 14, 16, '331', style10)
                sheet.write_merge(c+83, c+83, 17, 19, '', style10)
                sheet.write_merge(c+83, c+83, 20, 23, oc_331, style10)
                sheet.write_merge(c+83, c+83, 24, 27,ic_331 , style10)     
                    
                sheet.write_merge(c+84, c+84, 1, 13, '2. Người mua trả tiền trước dài hạn', style13)
                sheet.write_merge(c+84, c+84, 14, 16, '332', style10)
                sheet.write_merge(c+84, c+84, 17, 19, '', style10)
                sheet.write_merge(c+84, c+84, 20, 23, oc_332, style10)
                sheet.write_merge(c+84, c+84, 24, 27, ic_332, style10)
                
                sheet.write_merge(c+85, c+85, 1, 13, '3. Chi phí phải trả dài hạn', style13)
                sheet.write_merge(c+85, c+85, 14, 16, '333', style10)
                sheet.write_merge(c+85, c+85, 17, 19, '', style10)
                sheet.write_merge(c+85, c+85, 20, 23, oc_333, style10)
                sheet.write_merge(c+85, c+85, 24, 27,ic_333 , style10)                
                
                sheet.write_merge(c+86, c+86, 1, 13, '4. Phải trả nội bộ về vốn kinh doanh', style13)
                sheet.write_merge(c+86, c+86, 14, 16, '334', style10)
                sheet.write_merge(c+86, c+86, 17, 19, '', style10)
                sheet.write_merge(c+86, c+86, 20, 23, oc_334, style10)
                sheet.write_merge(c+86, c+86, 24, 27, ic_334, style10)     
                    
                sheet.write_merge(c+87, c+87, 1, 13, '5. Phải trả nội bộ dài hạn', style13)
                sheet.write_merge(c+87, c+87, 14, 16, '335', style10)
                sheet.write_merge(c+87, c+87, 17, 19, '', style10)
                sheet.write_merge(c+87, c+87, 20, 23,oc_335 , style10)
                sheet.write_merge(c+87, c+87, 24, 27, ic_335, style10)
                                  
                sheet.write_merge(c+88, c+88, 1, 13, '6. Doanh thu chưa thực hiện dài hạn', style13)
                sheet.write_merge(c+88, c+88, 14, 16, '336', style10)
                sheet.write_merge(c+88, c+88, 17, 19, '', style10)
                sheet.write_merge(c+88, c+88, 20, 23, oc_336, style10)
                sheet.write_merge(c+88, c+88, 24, 27,ic_336 , style10)     
                    
                sheet.write_merge(c+89, c+89, 1, 13, '7. Phải trả dài hạn khác', style13)
                sheet.write_merge(c+89, c+89, 14, 16, '337', style10)
                sheet.write_merge(c+89, c+89, 17, 19, '', style10)
                sheet.write_merge(c+89, c+89, 20, 23,oc_337 , style10)
                sheet.write_merge(c+89, c+89, 24, 27,ic_337 , style10)
                
                sheet.write_merge(c+90, c+90, 1, 13, '8. Vay và nợ thuế tài chính dài hạn', style13)
                sheet.write_merge(c+90, c+90, 14, 16, '338', style10)
                sheet.write_merge(c+90, c+90, 17, 19, '', style10)
                sheet.write_merge(c+90, c+90, 20, 23,oc_338 , style10)
                sheet.write_merge(c+90, c+90, 24, 27, ic_338, style10)                
                
                sheet.write_merge(c+91, c+91, 1, 13, '9. Trái phiếu chuyển đổi', style13)
                sheet.write_merge(c+91, c+91, 14, 16, '339', style10)
                sheet.write_merge(c+91, c+91, 17, 19, '', style10)
                sheet.write_merge(c+91, c+91, 20, 23, oc_339, style10)
                sheet.write_merge(c+91, c+91, 24, 27, ic_339, style10)     
                    
                sheet.write_merge(c+92, c+92, 1, 13, '10. Cổ phiếu ưu đãi', style13)
                sheet.write_merge(c+92, c+92, 14, 16, '340', style10)
                sheet.write_merge(c+92, c+92, 17, 19, '', style10)
                sheet.write_merge(c+92, c+92, 20, 23, oc_340, style10)
                sheet.write_merge(c+92, c+92, 24, 27,ic_340 , style10)

                sheet.write_merge(c+93, c+93, 1, 13, '11. Thuế thu nhập hoãn lại phải trờ', style13)
                sheet.write_merge(c+93, c+93, 14, 16, '341', style10)
                sheet.write_merge(c+93, c+93, 17, 19, '', style10)
                sheet.write_merge(c+93, c+93, 20, 23,oc_341 , style10)
                sheet.write_merge(c+93, c+93, 24, 27,ic_341 , style10)
                
                sheet.write_merge(c+94, c+94, 1, 13, '12. Dự phòng phải trả dài hạn', style13)
                sheet.write_merge(c+94, c+94, 14, 16, '342', style10)
                sheet.write_merge(c+94, c+94, 17, 19, '', style10)
                sheet.write_merge(c+94, c+94, 20, 23,oc_342 , style10)
                sheet.write_merge(c+94, c+94, 24, 27, ic_342, style10)                
                
                sheet.write_merge(c+95, c+95, 1, 13, '13. Quỹ phát triển khoa học và công nghệ', style13)
                sheet.write_merge(c+95, c+95, 14, 16, '343', style10)
                sheet.write_merge(c+95, c+95, 17, 19, '', style10)
                sheet.write_merge(c+95, c+95, 20, 23,oc_343 , style10)
                sheet.write_merge(c+95, c+95, 24, 27, ic_343, style10)     

                sheet.write_merge(c+96, c+96, 1, 13, 'D - VỐN CHỦ SỞ HỮU', style14)
                sheet.write_merge(c+96, c+96, 14, 16, '400', style10)
                sheet.write_merge(c+96, c+96, 17, 19, '', style10)
                sheet.write_merge(c+96, c+96, 20, 23, oc_400, style10)
                sheet.write_merge(c+96, c+96, 24, 27, ic_400, style10)
              
                sheet.write_merge(c+97, c+97, 1, 13, 'I. Vốn chủ sở hữu', style14)
                sheet.write_merge(c+97, c+97, 14, 16, '410', style10)
                sheet.write_merge(c+97, c+97, 17, 19, '', style10)
                sheet.write_merge(c+97, c+97, 20, 23,oc_410 , style10)
                sheet.write_merge(c+97, c+97, 24, 27, ic_410, style10)
                
                   
                sheet.write_merge(c+98, c+98, 1, 13, '1. Vốn góp của chủ sở hữu', style13)
                sheet.write_merge(c+98, c+98, 14, 16, '411', style10)
                sheet.write_merge(c+98, c+98, 17, 19, '', style10)
                sheet.write_merge(c+98, c+98, 20, 23,oc_411 , style10)
                sheet.write_merge(c+98, c+98, 24, 27, ic_411, style10)
                
                sheet.write_merge(c+99, c+99, 1, 13, '- Cổ phiếu phổ thông có quyền biểu quyết', style13)
                sheet.write_merge(c+99, c+99, 14, 16, '411a', style10)
                sheet.write_merge(c+99, c+99, 17, 19, '', style10)
                sheet.write_merge(c+99, c+99, 20, 23, oc_411a, style10)
                sheet.write_merge(c+99, c+99, 24, 27,ic_411a , style10)                
                
                sheet.write_merge(c+100, c+100, 1, 13, '- Cổ phiếu ưu đãi', style13)
                sheet.write_merge(c+100, c+100, 14, 16, '411b', style10)
                sheet.write_merge(c+100, c+100, 17, 19, '', style10)
                sheet.write_merge(c+100, c+100, 20, 23, oc_411b, style10)
                sheet.write_merge(c+100, c+100, 24, 27, ic_411b, style10)     


                sheet.write_merge(c+101, c+101, 1, 13, '2. Thặng dư vốn cổ phần', style13)
                sheet.write_merge(c+101, c+101, 14, 16, '412', style10)
                sheet.write_merge(c+101, c+101, 17, 19, '', style10)
                sheet.write_merge(c+101, c+101, 20, 23, oc_412, style10)
                sheet.write_merge(c+101, c+101, 24, 27, ic_412, style10)
                
                sheet.write_merge(c+102, c+102, 1, 13, '3. Quyền chọn chuyển đổi trái phiếu', style13)
                sheet.write_merge(c+102, c+102, 14, 16, '413', style10)
                sheet.write_merge(c+102, c+102, 17, 19, '', style10)
                sheet.write_merge(c+102, c+102, 20, 23,oc_413 , style10)
                sheet.write_merge(c+102, c+102, 24, 27,ic_413 , style10)                
                
                sheet.write_merge(c+103, c+103, 1, 13, '4. Vốn khác của chủ sở hữu', style13)
                sheet.write_merge(c+103, c+103, 14, 16, '414', style10)
                sheet.write_merge(c+103, c+103, 17, 19, '', style10)
                sheet.write_merge(c+103, c+103, 20, 23, oc_414, style10)
                sheet.write_merge(c+103, c+103, 24, 27, ic_414, style10)         
                            
                sheet.write_merge(c+104, c+104, 1, 13, '5. Cổ phiếu quỹ (*)', style13)
                sheet.write_merge(c+104, c+104, 14, 16, '415', style10)
                sheet.write_merge(c+104, c+104, 17, 19, '', style10)
                sheet.write_merge(c+104, c+104, 20, 23,oc_415 , style10)
                sheet.write_merge(c+104, c+104, 24, 27, ic_415, style10)
                
                sheet.write_merge(c+105, c+105, 1, 13, '6. Chênh lệch đánh giá lại tài sản', style13)
                sheet.write_merge(c+105, c+105, 14, 16, '416', style10)
                sheet.write_merge(c+105, c+105, 17, 19, '', style10)
                sheet.write_merge(c+105, c+105, 20, 23,oc_416 , style10)
                sheet.write_merge(c+105, c+105, 24, 27,ic_416 , style10)                
                
                sheet.write_merge(c+106, c+106, 1, 13, '7. Chênh lệch tỷ giá đối đoái', style13)
                sheet.write_merge(c+106, c+106, 14, 16, '417', style10)
                sheet.write_merge(c+106, c+106, 17, 19, '', style10)
                sheet.write_merge(c+106, c+106, 20, 23,oc_417 , style10)
                sheet.write_merge(c+106, c+106, 24, 27, ic_417, style10)     


                sheet.write_merge(c+107, c+107, 1, 13, '8. Quỹ đầu tư phát triển', style13)
                sheet.write_merge(c+107, c+107, 14, 16, '418', style10)
                sheet.write_merge(c+107, c+107, 17, 19, '', style10)
                sheet.write_merge(c+107, c+107, 20, 23,oc_418 , style10)
                sheet.write_merge(c+107, c+107, 24, 27,ic_418 , style10)
                
                sheet.write_merge(c+108, c+108, 1, 13, '9. Quỹ hỗ tợ sắp xếp doanh nghiệp', style13)
                sheet.write_merge(c+108, c+108, 14, 16, '419', style10)
                sheet.write_merge(c+108, c+108, 17, 19, '', style10)
                sheet.write_merge(c+108, c+108, 20, 23,oc_419 , style10)
                sheet.write_merge(c+108, c+108, 24, 27,ic_419 , style10)                
                
                sheet.write_merge(c+109, c+109, 1, 13, '10. Quỹ khác thuộc vốn chủ sở hữu', style13)
                sheet.write_merge(c+109, c+109, 14, 16, '420', style10)
                sheet.write_merge(c+109, c+109, 17, 19, '', style10)
                sheet.write_merge(c+109, c+109, 20, 23, oc_420, style10)
                sheet.write_merge(c+109, c+109, 24, 27,ic_420 , style10)         
               
                sheet.write_merge(c+110, c+110, 1, 13, '11. Lợi nhuận sau thuế chưa phân phối', style13)
                sheet.write_merge(c+110, c+110, 14, 16, '421', style10)
                sheet.write_merge(c+110, c+110, 17, 19, '', style10)
                sheet.write_merge(c+110, c+110, 20, 23, oc_421, style10)
                sheet.write_merge(c+110, c+110, 24, 27,ic_421 , style10)     


                sheet.write_merge(c+111, c+111, 1, 13, '- LNST chưa phân phối lũy kế đến cuối kỳ trước', style13)
                sheet.write_merge(c+111, c+111, 14, 16, '421a', style10)
                sheet.write_merge(c+111, c+111, 17, 19, '', style10)
                sheet.write_merge(c+111, c+111, 20, 23, oc_421a, style10)
                sheet.write_merge(c+111, c+111, 24, 27, ic_421a, style10)
                
                sheet.write_merge(c+112, c+112, 1, 13, 'LNST chưa phân phối kỳ này', style13)
                sheet.write_merge(c+112, c+112, 14, 16, '421b', style10)
                sheet.write_merge(c+112, c+112, 17, 19, '', style10)
                sheet.write_merge(c+112, c+112, 20, 23,od_421b , style10)
                sheet.write_merge(c+112, c+112, 24, 27, id_421b, style10)                
                
                sheet.write_merge(c+113, c+113, 1, 13, '12. Nguồn vốn đầu tư XDCB', style13)
                sheet.write_merge(c+113, c+113, 14, 16, '422', style10)
                sheet.write_merge(c+113, c+113, 17, 19, '', style10)
                sheet.write_merge(c+113, c+113, 20, 23,oc_422 , style10)
                sheet.write_merge(c+113, c+113, 24, 27,ic_422 , style10)        
                           
                sheet.write_merge(c+114, c+114, 1, 13, 'II. Nguồn kinh phí và quỹ khác', style14)
                sheet.write_merge(c+114, c+114, 14, 16, '430', style10)
                sheet.write_merge(c+114, c+114, 17, 19, '', style10)
                sheet.write_merge(c+114, c+114, 20, 23, oc_430, style10)
                sheet.write_merge(c+114, c+114, 24, 27, ic_430, style10)     


                sheet.write_merge(c+115, c+115, 1, 13, '1. Nguồn kinh phí', style13)
                sheet.write_merge(c+115, c+115, 14, 16, '431', style10)
                sheet.write_merge(c+115, c+115, 17, 19, '', style10)
                sheet.write_merge(c+115, c+115, 20, 23,oc_431 , style10)
                sheet.write_merge(c+115, c+115, 24, 27, ic_431, style10)
                
                sheet.write_merge(c+116, c+116, 1, 13, '2. Nguồn kính phí đã hình thành TSCĐ', style13)
                sheet.write_merge(c+116, c+116, 14, 16, '432', style10)
                sheet.write_merge(c+116, c+116, 17, 19, '', style10)
                sheet.write_merge(c+116, c+116, 20, 23,oc_432 , style10)
                sheet.write_merge(c+116, c+116, 24, 27,ic_432 , style10)                
                
                sheet.write_merge(c+117, c+117, 1, 13, 'TỔNG CỘNG NGUỒN VỐN (440 = 300 + 400)', style14)
                sheet.write_merge(c+117, c+117, 14, 16, '440', style10)
                sheet.write_merge(c+117, c+117, 17, 19, '', style10)
                sheet.write_merge(c+117, c+117, 20, 23,oc_440 , style10)
                sheet.write_merge(c+117, c+117, 24, 27,ic_440 , style10)        
                  
                filename = ('%s'+ '.xls') %(self._name)
                workbook.save(r'%s%s' %(path,filename))
                fp = open(r'%s%s' %(path,filename), "rb")
                file_data = fp.read()
                out = base64.encodestring(file_data)                                                 
                            
                # Files actions         
                attach_vals = {
                        'all_balance_data': self._name + '.xls',
                        'file_name': out,
                    }
                    
                act_id = self.env['account.all.balance.sheet'].create(attach_vals)
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
class AllBalanceSheetView(models.AbstractModel):
    _name='report.smart_invoice.all_balance_sheet_display'

    @api.model
    def _get_report_values(self,docids,data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= '%s %s' % (end_date, '23:59:59')
        filter_date=data['form']['filter_date']
        docs = []
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
        self.acc_balance = self.env.cr.fetchall()



        od_100 = 0
        id_100=0
        qw_100 = []
          
        od_110 = 0
        id_110=0
        qw_110 = []
        
        od_111 = 0
        id_111 = 0
        qw_111 = []

        od_112 = 0
        id_112 = 0
        qw_112 = []
        
        od_120 = 0
        id_120 = 0
        qw_120 = []
        

        od_121 = 0
        id_121 = 0
        qw_121 = []

        od_122 = 0
        id_122 = 0
        qw_122 = []

        od_123 = 0
        id_123 = 0
        qw_123 = []



        od_130 = 0
        id_130 = 0
        qw_130 = []

        od_131 = 0
        id_131 = 0
        qw_131 = []

        od_132 = 0
        id_132 = 0
        qw_132 = []

        od_133 = 0
        id_133 = 0
        qw_133 = []

        od_134 = 0
        id_134 = 0
        qw_134 = []

        od_135 = 0
        id_135 = 0
        qw_135 = []

        od_136 = 0
        id_136 = 0
        qw_136 = []

        oc_137 = 0
        ic_137 = 0
        qw_137 = []

        od_139 = 0
        id_139 = 0
        qw_139 = []

        od_140 = 0
        id_140 = 0
        qw_140 = []

        od_141 = 0
        id_141 = 0
        qw_141 = []

        oc_149 = 0
        ic_149 = 0
        qw_149 = []

        od_150 = 0
        id_150 = 0
        qw_150 = []

        od_151 = 0
        id_151 = 0
        qw_151 = []

        od_152 = 0
        id_152 = 0
        qw_152 = []

        od_153 = 0
        id_153 = 0
        qw_153 = []
        
        od_154 = 0
        id_154 = 0
        qw_154 = []
        
        od_155 = 0
        id_155 = 0
        qw_155 = []
        
        od_200 = 0
        id_200 = 0
        qw_200 = []

        od_210 = 0
        id_210 = 0
        qw_210 = []

        od_211 = 0
        id_211 = 0
        qw_211 = []

        od_212 = 0
        id_212= 0
        qw_212 = []

        od_213 = 0
        id_213 = 0
        qw_213 = []

        od_214 = 0
        id_214= 0
        qw_214 = []

        od_215= 0
        id_215= 0
        qw_215= []

        od_216= 0
        id_216= 0
        qw_216 = []

        oc_219= 0
        ic_219= 0
        qw_219= []


        od_200= 0
        id_200= 0
        qw_200 = []


        od_220= 0
        id_220= 0
        qw_220 = []

        od_221= 0
        id_221= 0
        qw_221 = []

        od_222= 0
        id_222= 0
        qw_222 = []

        oc_223= 0
        ic_223= 0
        qw_223= []

        od_224= 0
        id_224= 0
        qw_224 = []

        od_225= 0
        id_225 = 0
        qw_225= []

        oc_226= 0
        ic_226= 0
        qw_226 = []
        
        od_227= 0
        id_227= 0
        qw_227 = []

        od_228 =0
        id_228 = 0
        qw_228 =[]

        oc_229= 0
        ic_229 =0
        qw_229 = []

        od_230= 0
        id_230= 0
        qw_230 = []

        od_231= 0
        id_231= 0
        qw_231= []

        oc_232= 0
        ic_232= 0
        qw_232= []

        od_240= 0
        id_240= 0
        qw_240 = []

        od_241= 0
        id_241= 0
        qw_241= []

        od_242= 0
        id_242= 0
        qw_242= []

        od_250= 0
        id_250= 0
        qw_250= []

        od_251= 0
        id_251= 0
        qw_251= []

        od_252= 0
        id_252= 0
        qw_252= []

        od_253= 0
        id_253= 0
        qw_253= []
        
 
        oc_254= 0
        ic_254= 0
        qw_254= []       
        
 
        od_255= 0
        id_255= 0
        qw_255 = []

        od_260 = 0
        id_260 = 0
        qw_260 = []

        od_261 = 0
        id_261 = 0
        qw_261 = []
           
        od_262 = 0
        id_262 = 0
        qw_262 = []

        od_263 = 0
        id_263 = 0
        qw_263 = []

        od_268 = 0
        id_268 = 0
        qw_268 = []



        od_270 = 0
        id_270 = 0
        qw_270 = []

        oc_300 = 0
        ic_300 = 0
        qw_300 = []
        
        oc_310 = 0
        ic_310 = 0
        qw_310 = []


        oc_330 = 0
        ic_330 = 0
        qw_330 = []

        oc_311 = 0
        ic_311 = 0
        qw_311 = []

        oc_312 = 0
        ic_312 = 0
        qw_312 = []

        oc_313 = 0
        ic_313 = 0
        qw_313 = []    

        oc_314 = 0
        ic_314 = 0
        qw_314 = []

        oc_315 = 0
        ic_315 = 0
        qw_315 = []

        oc_316 = 0
        ic_316 = 0
        qw_316 = []

        oc_317 = 0
        ic_317 = 0
        qw_317 = []
                
        oc_318 = 0
        ic_318= 0
        qw_318 = []
 
        oc_319 = 0
        ic_319 = 0
        qw_319 = []

        oc_320 = 0
        ic_320 = 0
        qw_320 = []
                
        oc_321 = 0
        ic_321 = 0
        qw_321 = []
               
        oc_322 = 0
        ic_322 = 0
        qw_322 = []
 
        oc_323 = 0
        ic_323 = 0
        qw_323 = []
               
     
        oc_324 = 0
        ic_324 = 0
        qw_324 = []    
        
        oc_331 = 0
        ic_331 = 0
        qw_331 = []          

        oc_332 = 0
        ic_332 = 0
        qw_332 = []          
               
        oc_333 = 0
        ic_333 = 0
        qw_333 = []          
                
        oc_334 = 0
        ic_334 = 0
        qw_334 = []          
                
        oc_335 = 0
        ic_335 = 0
        qw_335 = []

        oc_336 = 0
        ic_336 = 0
        qw_336 = []
               
        oc_337 = 0
        ic_337 = 0
        qw_337 = []          
                                
        oc_338 = 0
        ic_338 = 0
        qw_338 = []          
                
        oc_339 = 0
        ic_339 = 0
        qw_339 = []
            
        oc_340 = 0
        ic_340 = 0
        qw_340 = []          
                        
        oc_341 = 0
        ic_341 = 0
        qw_341 = []
               
        oc_342 = 0
        ic_342 = 0
        qw_342 = []
               
        oc_343 = 0
        ic_343 = 0
        qw_343 = []

        oc_411a = 0
        ic_411a = 0
        qw_411a= []

        oc_411b = 0
        ic_411b = 0
        qw_411b = []

        oc_412 = 0
        ic_412 = 0
        qw_412= []

        oc_413 = 0
        ic_413 = 0
        qw_413 = []        

        oc_414 = 0
        ic_414 = 0
        qw_414 = []
        

        oc_415 = 0
        ic_415 = 0
        qw_415 = []
        
        oc_416 = 0
        ic_416 = 0
        qw_416 = []
        

        oc_417 = 0
        ic_417 = 0
        qw_417 = []

        oc_418 = 0
        ic_418 = 0
        qw_418 = []

        oc_419= 0
        ic_419= 0
        qw_419= []      
                                                                            

        oc_420 = 0
        ic_420 = 0
        qw_420 = []

 
        oc_421a = 0
        ic_421a = 0
        qw_421a= []       

 
        od_421b = 0
        id_421b = 0
        qw_421b = []
        


        oc_422 = 0
        ic_422 = 0
        qw_422 = []


        oc_431 = 0
        ic_431 = 0
        qw_431 = []


        oc_432 = 0
        ic_432 = 0
        qw_432 = []


        oc_440 = 0
        ic_440 = 0
        qw_440 = []

        oc_400 = 0
        ic_400 = 0
        qw_400 = []


        oc_410 = 0
        ic_410 = 0
        qw_410 = []



        oc_411 = 0
        ic_411 = 0
        qw_411 = []


        oc_421 = 0
        ic_421 = 0
        qw_421 = []


        oc_430 = 0
        ic_430 = 0
        qw_430 = []

        _isMoney = True
        # _time = 2


        for item in self.acc_balance:
            x = item[6]
            _time = relativedelta(x, datetime.strptime(start_date,'%Y-%m-%d')).months
            if item[0] == '1111':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1112':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1113':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1121':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1122':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1123':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1131':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1132':
                od_111 += item[2]
                id_111 += item[4]

            if item[0] == '1281' and _time <3:
                od_112 += item[2]
                id_112 += item[4]

            if item[0] == '1288' and  _time <3:
                od_112 += item[2]
                id_112 += item[4]

            if item[0] == '1211':
                od_121 += item[2]
                id_121 += item[4]

            if item[0] == '1212':
                od_121 += item[2]
                id_121 += item[4]

            if item[0] == '1218':
                od_121 += item[2]
                id_121 += item[4]

            if item[0] == '2291':
                od_122 += item[3]
                id_122 += item[5]

            if item[0] == '1281' and _isMoney== False and _time <12:
                od_123 += item[2]
                id_123 += item[4]

            if item[0] == '1282' and _isMoney== False and _time <12:
                od_123 += item[2]
                id_123 += item[4]

            if item[0] == '1288' and _isMoney== False and _time <12:
                od_123 += item[2]
                id_123 += item[4]

            if item[0] == '131' and _time <12:
                od_131 += item[2]
                id_131 += item[4]


            if item[0] == '331' and _time<12:
                od_132 += item[2]
                id_132 += item[4]

            if item[0] == '1362' and _time<12:
                od_133 += item[2]
                id_133 += item[4]

            if item[0] == '1363' and _time<12:
                od_133 += item[2]
                id_133 += item[4]

            if item[0] == '1368' and _time<12:
                od_133 += item[2]
                id_133 += item[4]

            if item[0] == '337':
                od_134 += item[2]
                id_134 += item[4]

            if item[0] == '1283' and _time<12:
                od_135 += item[2]
                id_135 += item[4]

            if item[0] == '1385' and _time<12:
                od_136 += item[2]
                id_136 += item[4]

            if item[0] == '1388' and _time<12:
                od_136 += item[2]
                id_136 += item[4]
                
            if item[0] == '3341' and _time<12:
                od_136 += item[2]
                id_136 += item[4]
                         
            if item[0] == '3348' and _time<12:
                od_136 += item[2]
                id_136 += item[4]
                          
            if item[0] == '3381' and _time<12:
                od_136 += item[2]
                id_136 += item[4]
                           
            if item[0] == '3388' and _time<12:
                od_136 += item[2]
                id_136 += item[4]
                           
            if item[0] == '141' and _time<12:
                od_136 += item[2]
                id_136 += item[4]

            if item[0] == '244' and _time<12:
                od_136 += item[2]
                id_136 += item[4]

            if item[0] == '2293':
                oc_137+= item[3]
                ic_137 += item[5]
            
            if item[0] == '1381':
                od_139+= item[2]
                id_139 += item[4]

            if item[0] == "151":
                od_141 += item[2]
                id_141 += item[4]

            if item[0] == "1531":
                od_141 += item[2]
                id_141 += item[4]

            if item[0] == "1532":
                od_141 += item[2]
                id_141 += item[4]

            if item[0] == "1533":
                od_141 += item[2]
                id_141 += item[4]

            if item[0] == "1534":
                od_141 += item[2]
                id_141 += item[4]
            if item[0] == "1551":
                od_141 += item[2]
                id_141 += item[4]

            if item[0] == "1557":
                od_141+= item[2]
                id_141+= item[4]

            if item[0] == "1561":
                od_141 += item[2]
                id_141 += item[4]

            if item[0] == "1562":
                od_141 += item[2]
                id_141 += item[4]

            if item[0] == "1567":
                od_141 += item[2]
                id_141 += item[4]
            
            if item[0] == "2294":
                oc_149 += item[3]
                ic_149 += item[5]
            
            if item[0] == "2421" and _time<12:
                od_151 += item[2]
                id_151 += item[4]
            
            if item[0] == "1331":
                od_152 += item[2]
                id_152 += item[4]

            if item[0] == "1332":
                od_152 += item[2]
                id_152 += item[4]

            if item[0] == '3331':
                od_153 += item[2]
                id_153 += item[4]

            if item[0] == '33311':
                od_153 += item[2]
                id_153 += item[4]                

            if item[0] == '33312':
                od_153 += item[2]
                id_153 += item[4]                        

            if item[0] == '3332':
                od_153 += item[2]
                id_153 += item[4]

            if item[0] == '3333':
                od_153 += item[2]
                id_153 += item[4]


            if item[0] == '3334':
                od_153 += item[2]
                id_153 += item[4]

            if item[0] == '3335':
                od_153 += item[2]
                id_153 += item[4]

            if item[0] == '3336':
                od_153 += item[2]
                id_153 += item[4]

            if item[0] == '3337':
                od_153 += item[2]
                id_153 += item[4]

            if item[0] == '33381':
                od_153 += item[2]
                id_153 += item[4]

            if item[0] == '33382':
                od_153 += item[2]
                id_153 += item[4]


            if item[0] == '3339':
                od_153 += item[2]
                id_153 += item[4]                              
            
            if item[0] == '171':
                od_154 += item[2]
                id_154 +=item[4]
                
            if item[0] == '2288':
                od_155 += item[2]
                id_155 += item[4]

            if item[0] == '131':
                od_211 += item[2]
                id_211 += item[4]

            if item[0] == '331' and _time >12:
                od_212 += item[2],
                id_212 += item[4]

            if item[0] == '1361':
                od_213 += item[2]
                id_213 += item[4]

            if item[0] == '1362' and _time >12:
                od_214 += item[2]
                id_214 += item[4]                

            if item[0] == '1363' and _time >12:
                od_214 += item[2]
                id_214 += item[4]      

            if item[0] == '1368' and _time >12:
                od_214 += item[2]
                id_214 += item[4]

            if item[0] == '1283' and _time >12:
                od_215 += item[2]
                id_215 += item[4]

            if item[0] == '1385':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '1388':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3341':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3348':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3381':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3382':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3383':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3384':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3385':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3386':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3387':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3388':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3341':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '3348':
                od_216 += item[2]
                id_216 += item[4]

            if item[0] == '2293':
                oc_219 += item[3]
                ic_219 += item[5]
            
            if item[0] == '2111':
                od_222 += item[2]
                id_222 += item[4]
            if item[0] == '2112':
                od_222 += item[2]
                id_222 += item[4]                                                                                
                
            if item[0] == '2113':
                od_222 += item[2]
                id_222 += item[4]

            if item[0] == '2114':
                od_222 += item[2]
                id_222 += item[4]
                                                                                            
            if item[0] == '2115':
                od_222 += item[2]
                id_222 += item[4]

            if item[0] == '2118':
                od_222 += item[2]
                id_222 += item[4]       

            if item[0]=='2141':
                oc_223 += item[3]                                                                   
                ic_223 += item[5]    

            if item[0] == '2121' :
                od_225 += item[2]
                id_225 += item[4]
            

            if item[0] == '2122':
                od_225 += item[2]
                id_225 += item[4]           

            if item[0] == '2142':
                oc_226 += item[3]
                ic_226 += item[5]
                                                                             
            # if item[0] == '':
            #     od_228 += item[2]
            #     id_228 += item[4]                                                                    
            # if item[0] == '':
            #     od_228 += item[2]
            #     id_228 += item[4]                                     
                
            if item[0] == '2131':
                od_228 += item[2]
                id_228 += item[4]
                 
            if item[0] == '2132':
                od_228 += item[2]
                id_228 += item[4]                     
            if item[0] == '2133':
                od_228 += item[2]
                id_228 += item[4]     
            if item[0] == '2134':
                od_228 += item[2]
                id_228 += item[4]     

            if item[0] == '2135':
                od_228 += item[2]
                id_228 += item[4]
                   
            if item[0] == '2136':
                od_228 += item[2]
                id_228 += item[4]
                 
            if item[0] == '2138':
                od_228 += item[2]
                id_228 += item[4]
            
            if item[0] == '2143':
                oc_229 += item[3]
                ic_229 += item[5]     
            
            if item[0] == '217':
                od_231 += item[2]
                id_231 += item[4]

            if item[0] == '2147':
                oc_232 += item[3]
                ic_232 += item[5]

            if item[0] == '154' and _time > 12:
                od_241 += item[2]
                id_241 += item[4]

            if item[0] == '2294' and _time > 12:
                od_241 += item[3]
                id_241 += item[5]
            
            if item[0]=='2411' or item[0]=='2412' or item[0]=='2413':
                od_242 += item[2]
                id_242 += item[4]

            if item[0]=='221':
                od_251 += item[2]
                id_251 += item[4]

            if item[0]=='222':
                od_252 += item[2]
                id_252 += item[4]

            if item[0]=='2281':
                od_253 += item[2]
                id_253 += item[4]
                          
            if item[0]=='2292':
                oc_254 += item[3]
                ic_254 += item[5]

            if item[0]=='1281': #and _time >12:
                od_255 += item[2]
                id_255 += item[4]

            if item[0]=='1282': #and _time >12:
                od_255 += item[2]
                id_255 += item[4]

            if item[0]=='1288':# and _time >12:
                od_255 += item[2]
                id_255 += item[4]

            if item[0] == '242' and _time > 12:
                od_261 += item[2]
                id_261 += item[4]


            if item[0] == '243' :
                od_262 += item[2]
                id_262 += item[4]

            if item[0] == '1534' :
                od_263 += item[2]
                id_263 += item[4]

            if item[0] == '2294' :
                od_263 += item[3]
                id_263 += item[5]

            if item[0] == '2288' :
                od_268 += item[2]
                id_268 += item[4]
            
            if item[0] == '331' and _time <12:
                oc_311 += item[3]
                ic_311 += item[5]

            if item[0] == '131' and _time<12:
                oc_312 += item[3]
                ic_312 += item[5]

            if item[0] == '3331':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '33311':
                oc_313 += item[3]
                ic_313 += item[5]          

            if item[0] == '33312':
                oc_313 += item[3]
                ic_313 += item[5]                   

            if item[0] == '3332':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '3333':
                oc_313 += item[3]
                ic_313 += item[5]


            if item[0] == '3334':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '3335':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '3336':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '3337':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '33381':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '33382':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '3339':
                oc_313 += item[3]
                ic_313 += item[5]

            if item[0] == '3341':
                oc_314 += item[3]
                ic_314 += item[5]

            if item[0] == '3348':
                oc_314 += item[3]
                ic_314 += item[5]

            if item[0] == '335' and _time <12:
                oc_315 += item[3]
                ic_315 += item[5]
                           
            if item[0] == '3361':
                oc_316 += item[3]
                ic_316 += item[5]
                
            if item[0] == '3363':
                oc_316 += item[3]
                ic_316 += item[5]
                
            if item[0] == '3368':
                oc_316 += item[3]
                ic_316 += item[5]

            if item[0] == '337':
                oc_317 += item[3]
                ic_317 += item[5]

            if item[0] == '3387' and _time<12:
                oc_318 += item[3]
                ic_318 += item[5]

            if item[0] == '3381':
                oc_319 += item[3]
                ic_319 += item[5]
  

            if item[0] == '3382':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '3383':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '3384':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '3385':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '3386':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '3387':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '3388':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '1381':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '1385':
                oc_319 += item[3]
                ic_319 += item[5]
  
            if item[0] == '1388':
                oc_319 += item[3]
                ic_319 += item[5]

            if item[0] == '3411' and _time <12:
                oc_320 += item[3]
                ic_320 += item[5]
  
            if item[0] == '3412' and _time <12:
                oc_320 += item[3]
                ic_320 += item[5]
  
            if item[0] == '34311' and _time <12:
                oc_320 += item[3]
                ic_320 += item[5]

            if item[0] == '3521':
                oc_321 += item[3]
                ic_321 += item[5]

            if item[0] == '3522':
                oc_321 += item[3]
                ic_321 += item[5]
  
            if item[0] == '3523':
                oc_321 += item[3]
                ic_321 += item[5]
  
            if item[0] == '3524':
                oc_321 += item[3]
                ic_321 += item[5]


            if item[0] == '3531':
                oc_322 += item[3]
                ic_322 += item[5]

            if item[0] == '3532':
                oc_322 += item[3]
                ic_322 += item[5]
  
            if item[0] == '3533':
                oc_322 += item[3]
                ic_322 += item[5]
  
            if item[0] == '3534':
                oc_322 += item[3]
                ic_322 += item[5]
                
            if item[0] == '357':
                oc_323 += item[3]
                ic_323 += item[5]

            if item[0] == '171':
                oc_324 += item[3]
                ic_324 += item[5]


            if item[0] == '331' and _time >12:
                oc_331 += item[3]
                ic_331 += item[5]

            if item[0] == '131' and _time >12:
                oc_332 += item[3]
                ic_332 += item[5]

            if item[0] == '335':
                oc_333 += item[3]
                ic_333 += item[5]

            if item[0] == '3361':
                oc_334 += item[3]
                ic_334 += item[5]

            if item[0] == '3362' and _time >12:
                oc_335 += item[3]
                ic_335 += item[5]

            if item[0] == '3363' and _time >12:
                oc_335 += item[3]
                ic_335 += item[5]

            if item[0] == '3368' and _time >12:
                oc_335 += item[3]
                ic_335 += item[5]

            if item[0] == '3387' and _time >12:
                oc_336 += item[3]
                ic_336 += item[5]

            if item[0] == '3381' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]                
            if item[0] == '3382' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]
            if item[0] == '3383' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]                        
            if item[0] == '3384' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]
                
            if item[0] == '3385' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]

            if item[0] == '3386' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]
            if item[0] == '3387' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]

            if item[0] == '344' and _time >12:
                oc_337 += item[3]
                ic_337 += item[5]

            if item[0] == '3411' and _time >12:
                oc_338 += item[3]
                ic_338 += item[5]

            if item[0] == '3412' and _time >12:
                oc_338 += item[3]
                ic_338 += item[5]

            if item[0] == '34312' and _time >12:
                oc_338 -= item[2]
                ic_338 -= item[4]    

            if item[0] == '34313' and _time >12:
                oc_338 += item[3]
                ic_338 += item[5]    


            if item[0] == '3432':
                oc_339 += item[3]
                ic_339 += item[5]    


            if item[0] == '41112':
                oc_340 += item[3]
                ic_340 += item[5]
                
            if item[0] == '347':
                oc_341 += item[3]
                ic_341 += item[5]

            if item[0] == '3521':
                oc_342 += item[3]
                ic_342 += item[5]

            if item[0] == '3522':
                oc_342 += item[3]
                ic_342 += item[5]

            if item[0] == '3523':
                oc_342 += item[3]
                ic_342 += item[5]

            if item[0] == '3524':
                oc_342 += item[3]
                ic_342 += item[5]

            if item[0] == '3561':
                oc_343 += item[3]
                ic_343 += item[5]

            if item[0] == '3562':
                oc_343 += item[3]
                ic_343 += item[5]

            if item[0] == '41111':
                oc_411a += item[3]
                ic_411a += item[5]
       
            if item[0] == '41112':
                oc_411b += item[3]
                ic_411b += item[5]      
        
            if item[0] == '4112':
                oc_412 += item[3]
                ic_412 += item[5]             

            if item[0] == '4113':
                oc_413 += item[3]
                ic_413 += item[5]

            if item[0] == '4118':
                oc_414 += item[3]
                ic_414 += item[5]
            

            if item[0] == '419':
                oc_415 += item[2]
                ic_415 += item[4]            


            if item[0] == '412':
                oc_416 += item[3]
                ic_416 += item[5]

            if item[0] == '4131':
                oc_417 += item[3]
                ic_417 += item[5]

            if item[0] == '4132':
                oc_417 += item[3]
                ic_417 += item[5]

            if item[0] == '414':
                oc_418 += item[3]
                ic_418 += item[5]

            if item[0] == '417':
                oc_419 += item[3]
                ic_419 += item[5]

            if item[0] == '418':
                oc_420 += item[3]
                ic_420 += item[5]

            if item[0] == '4211':
                oc_421a += item[3]
                ic_421a += item[5]

            if item[0] == '4212':
                od_421b += item[2]
                id_421b += item[4]

            if item[0] == '441':
                oc_422 += item[3]
                ic_422 += item[5]

            if item[0] == '4611':
                oc_431 += item[3]
                ic_431 += item[5]

            if item[0] == '4612':
                oc_431 += item[3]
                ic_431 += item[5]

            if item[0] == '1611':
                oc_431 -= item[2]
                ic_431 -= item[4]    

            if item[0] == '1612':
                oc_431 -= item[2]
                ic_431 -= item[4]

            if item[0] == '466':
                oc_432 += item[3]
                ic_432 += item[5]

        
        qw_111.append({
            'od_111': od_111,
            'id_111': id_111
        })
        
        qw_112.append({
            'od_112': od_112,
            'id_112':id_112
        })
        od_110 = od_111 + od_112
        id_110= id_111 + id_112
        qw_110.append({
             'od_110': od_110,
             'id_110' :id_110
        })
        od_120 = od_121 + od_122 + od_123
        id_120 = id_121 + id_122 + id_123
        qw_120.append({
            'od_120':od_120,
            'id_120':id_120
        })

        qw_121.append({
            'od_121': od_121,
            'id_121': id_121
            
        })
        qw_122.append({
            'od_122': od_122,
            'id_122':id_122
        })
        qw_123.append({
            'od_123': od_123,
            'id_123':id_123
        })
        od_130=od_131 + od_132 + od_133 + od_134 + od_135 + oc_137 + od_139 
        id_130=id_131 + id_132 + id_133 + id_134 + id_135 + ic_137 + id_139 
        qw_130.append({
            'od_130': od_130,
            'id_130': id_130
        })

        qw_131.append({
            'od_131': od_131,
            'id_131': id_131
        })

        qw_132.append({
            'od_132': od_132,
            'id_132':id_132
        })

        qw_133.append({
            'od_133': od_133,
            'id_133':id_133
        })
        qw_134.append({
            'od_134': od_134,
            'id_134':id_134
        })
        qw_135.append({
            'od_135': od_135,
            'id_135':id_135
        })

        qw_136.append({
            'od_136': od_136,
            'id_136':id_136
        })
        qw_137.append({
            'oc_137': oc_137,
            'ic_137':ic_137
        })
        qw_139.append({
            'od_139':od_139,
            'id_139':id_139
        })
        od_140 = od_141 + oc_149
        id_140 = id_141 + ic_149
        
        qw_140.append({
            'od_140': od_140,
            'id_140': id_140
        })

        qw_141.append({
            'od_141': od_141,
            'id_141': id_141
        })
        qw_149.append({
            'oc_149': oc_149,
            'ic_149': ic_149
        })
        od_150= od_151 + od_152 + od_153 + od_154 +od_155
        id_150= id_151 + id_152 + id_153 + id_154 +id_155

        qw_150.append({
            'od_150': od_150,
            'id_150': id_150
        })

        qw_151.append({
            'od_151': od_151,
            'id_151':id_151
        })
        qw_152.append({
            'od_152': od_152,
            'id_152': id_152
        })
        qw_153.append({
            'od_153': od_153,
            'id_153' :id_153
        })
        qw_154.append({
            'od_154': od_154,
            'id_154':id_154
        })
        qw_155.append({
            'od_155': od_155,
            'id_155':id_155
        })

        od_100 = od_110 + od_120 + od_130 + od_140 + od_150
        id_100 = id_110 + id_120 + id_130 + id_140 + id_150
        
        qw_100.append({
            'od_100': od_100,
            'id_100': id_100
        })

        od_210= od_211 + od_212 + od_213 + od_214 + od_215 + od_216 + oc_219
        id_210= id_211 + id_212 + id_213 + id_214 + id_215 + id_216 + ic_219
        qw_210.append({
            'od_210': od_210,
            'id_210': id_210
        })


        qw_211.append({
            'od_211': od_211,
            'id_211':id_211
        })
        qw_212.append({
            'od_212':od_212,
            'id_212':id_212
        })
        qw_213.append({
            'od_213': od_123,
            'id_213':id_213
        })
        qw_214.append({
            'od_214': od_214,
            'id_214':id_214
        })
        qw_215.append({
            'od_215': od_215,
            'id_215':id_215
        })
        qw_216.append({
            'od_216': od_216,
            'id_216': id_216
        })
        qw_219.append({
            'oc_219': oc_219,
            'ic_219':ic_219
        })

        

        od_221= od_222+ oc_223
        id_221= id_222+ ic_223
        qw_221.append({
            'od_221': od_221,
            'id_221' :id_221
        })

        qw_222.append({
            'od_222': od_222,
            'id_222' :id_222
            
        })
        qw_223.append({
            'oc_223': oc_223,
            'ic_223' :ic_223
        })
        od_224= od_225 +oc_226
        id_224= id_225 +ic_226
        qw_224.append({
            'od_224': od_224,
            'id_224' :id_224
        })
        qw_225.append({
            'od_225' :od_225,
            'id_225': id_225
        })

        qw_226.append({
            'oc_226':oc_226,
            'ic_226':ic_226
        })

        od_227=od_228 + oc_229
        id_227=id_228 + ic_229
        qw_227.append({
            'od_227':od_227,
            'id_227':id_227
        })

        qw_228.append({
            'od_228': od_228,
            'id_228' :id_228
        })

        qw_229.append({
            'oc_229' :oc_229,
            'ic_229': ic_229
        })
        od_230 = od_231 + oc_232
        id_230 = id_231 + ic_232
        qw_230.append({
            'od_230' :od_230,
            'id_230': id_230
        })

        qw_231.append({
            'od_231' :od_231,
            'id_231' :id_231
        })
        qw_232.append({
            'oc_232' : oc_232,
            'ic_232': ic_232
        })
        od_240= od_241 +od_242
        id_240= id_241 +id_242
        qw_240.append({
            'od_240': od_240,
            'id_240' :id_240
        })

        qw_241.append({
            'od_241': od_241,
            'id_241' :id_241
        })
        qw_242.append({
            'od_242': od_242,
            'id_242' :id_242
        })
        od_250= od_251 + od_252 + od_253 + oc_254 + od_255
        id_250= id_251 + id_252 + id_253 + ic_254 + id_255
        qw_250.append({
            'od_250': od_250,
            'id_250': id_250
            
        })
        qw_251.append({
            'od_251': od_251,
            'id_251': id_251
            
        })
        qw_252.append({
            'od_252': od_252,
            'id_252' :id_252
        })
        qw_253.append({
            'od_253': od_253,
            'id_253' :id_253
        })   
        qw_254.append({
            'oc_254': oc_254,
            'ic_254' :ic_254
        })    
        qw_255.append({
            'od_255': od_255,
            'id_255' :id_255
        })
        od_260= od_261 + od_262 + od_263 + od_268
        id_260= id_261 + id_262 + id_263 + id_268
        qw_260.append({
            'od_260': od_260,
            'id_260' :id_260
        })
        qw_261.append({
            'od_261': od_261,
            'id_261' :id_261
        })
        qw_262.append({
            'od_262': od_262,
            'id_262' :id_262
        })
        qw_263.append({
            'od_263': od_263,
            'id_263' :id_263
        })
        qw_268.append({
            'od_268': od_268,
            'id_268' :id_268
        })

        od_220= od_221 + od_224 + od_227
        id_220= id_221 + id_224 + id_227
        qw_220.append({
            'od_220': od_220,
            'id_220' :id_220
        })
        od_200= od_210 + od_220 + od_230 + od_240 + od_250 + od_260
        id_200= id_210 + id_220 + id_230 + id_240 + id_250 + id_260
        qw_200.append({
            'od_200': od_200,
            'id_200' :id_200
        })
        od_270= od_100 +od_200
        id_270= id_100 +id_200
        qw_270.append({
            'od_270': od_270,
            'id_270' :id_270
        })


        qw_311.append({
            'oc_311': oc_311,
            'ic_311':ic_311
        })
        qw_312.append({
            'oc_312': oc_312,
            'ic_312':ic_312
        })
        qw_313.append({
            'oc_313': oc_313,
            'ic_313':ic_313
        })
        qw_314.append({
            'oc_314': oc_314,
            'ic_314':ic_314
        })
        qw_315.append({
            'oc_315': oc_315,
            'ic_315':ic_315
        })
        qw_316.append({
            'oc_316': oc_316,
            'ic_316':ic_316
        })

        qw_317.append({
            'oc_317': oc_317,
            'ic_317':ic_317
        })
        qw_318.append({
            'oc_318': oc_318,
            'ic_318':ic_318
        })
        qw_319.append({
            'oc_319': oc_319,
            'ic_319':ic_319
        })
        qw_320.append({
            'oc_320': oc_320,
            'ic_320':ic_320
        })
                       
        qw_321.append({
            'oc_321': oc_321,
            'ic_321':ic_321
        })
        qw_322.append({
            'oc_322': oc_322,
            'ic_322':ic_322
        })
        qw_323.append({
            'oc_323': oc_323,
            'ic_323':ic_323
        })
                                                                    
        qw_324.append({
            'oc_324': oc_324,
            'ic_324':ic_324
        })
        oc_310= oc_311 + oc_312 + oc_313 + oc_314 + oc_315 + oc_316 + oc_317 + oc_318 + oc_319 + oc_320 + oc_321 + oc_322 + oc_323 + oc_324
        ic_310= ic_311 + ic_312 + ic_313 + ic_314 + ic_315 + ic_316 + ic_317 + ic_318 + ic_319 + ic_320 + ic_321 + ic_322 + ic_323 + ic_324
        qw_310.append({
            'oc_310': oc_310,
            'ic_310': ic_310
        })

              
        qw_331.append({
            'oc_331': oc_331,
            'ic_331': ic_331
        })

        qw_332.append({
            'oc_332': oc_332,
            'ic_332': ic_332
        })
        qw_333.append({
            'oc_333': oc_333,
            'ic_333': ic_333
        })
                        
        qw_334.append({
            'oc_334': oc_334,
            'ic_334': ic_334
        })
            
        qw_335.append({
            'oc_335': oc_335,
            'ic_335': ic_335
        })
        qw_336.append({
            'oc_336': oc_336,
            'ic_336': ic_336
        })
                        
        qw_337.append({
            'oc_337': oc_337,
            'ic_337': ic_337
        })
            
        qw_338.append({
            'oc_338': oc_338,
            'ic_338': ic_338
        })
            

        qw_339.append({
            'oc_339': oc_339,
            'ic_339': ic_339
        })
            

        qw_340.append({
            'oc_340': oc_340,
            'ic_340': ic_340
        })
            
        qw_341.append({
            'oc_341': oc_341,
            'ic_341': ic_341
        })
            
        qw_342.append({
            'oc_342': oc_342,
            'ic_342': ic_342
        })
            
        qw_343.append({
            'oc_343': oc_343,
            'ic_343': ic_343
        })
        oc_330= oc_331 + oc_332 + oc_333 + oc_334 + oc_335 + oc_336 + oc_337 + oc_338 + oc_339 + oc_340 + oc_341 + oc_342 + oc_343
        ic_330= ic_331 + ic_332 + ic_333 + ic_334 + ic_335 + ic_336 + ic_337 + ic_338 + ic_339 + ic_340 + ic_341 + ic_342 + ic_343
        qw_330.append({
            'oc_330': oc_330,
            'ic_330': ic_330
        })
        oc_300 = oc_310 + oc_330
        ic_300 = ic_310 + ic_330
        qw_300.append({
            'oc_300': oc_300,
            'ic_300': ic_300
        })


        qw_411a.append({
            'oc_411a': oc_411a,
            'ic_411a': ic_411a
        })

        qw_411b.append({
            'oc_411b': oc_411b,
            'ic_411b': ic_411b
        })
        oc_411 =oc_411a + oc_411b
        ic_411 =ic_411a + ic_411b
        qw_411.append({
            'oc_411':oc_411,
            'ic_411':ic_411
        })

        qw_412.append({
            'oc_412': oc_412,
            'ic_412': ic_412
        })
        qw_413.append({
            'oc_413': oc_413,
            'ic_413': ic_413
        })

        qw_414.append({
            'oc_414': oc_414,
            'ic_414': ic_414
        })


        qw_415.append({
            'oc_415': oc_415,
            'ic_415': ic_415
        })

        qw_416.append({
            'oc_416': oc_416,
            'ic_416': ic_416
        })

        qw_417.append({
            'oc_417': oc_417,
            'ic_417': ic_417
        })

        qw_418.append({
            'oc_418': oc_418,
            'ic_418': ic_418
        })
        
        qw_419.append({
            'oc_419': oc_419,
            'ic_419': ic_419
        })

        qw_420.append({
            'oc_420': oc_420,
            'ic_420': ic_420
        })


        qw_420.append({
            'oc_420': oc_420,
            'ic_420': ic_420
        })
        
        qw_421a.append({
            'oc_421a': oc_421a,
            'ic_421a': ic_421a
        })
        qw_421b.append({
            'od_421b': od_421b,
            'id_421b': id_421b
        })
        oc_421= oc_421a +  od_421b
        ic_421 = ic_421a + id_421b
        
        qw_421.append({
            'oc_421': oc_421,
            'ic_421':ic_421
        })
        
        qw_422.append({
            'oc_422': oc_422,
            'ic_422': ic_422
        })

        qw_431.append({
            'oc_431': oc_431,
            'ic_431': ic_431
        })

        qw_432.append({
            'oc_432': oc_432,
            'ic_432': ic_432
        })
        oc_430= oc_431 + oc_432
        ic_430= ic_431 + ic_432
        qw_430.append({
            'oc_430': oc_430,
            'ic_430': ic_430
        })
        oc_410=oc_411 + oc_412 + oc_413 + oc_414 + oc_415 + oc_416 + oc_417 + oc_418 + oc_419 + oc_420+oc_421 + oc_422
        ic_410=ic_411 + ic_412 + ic_413 + ic_414 + ic_415 + ic_416 + ic_417 + ic_418 + ic_419 + ic_420 + ic_421 + ic_422
        qw_410.append({
            'oc_410': oc_410,
            'ic_410': ic_410
        })
        oc_400= oc_410 + oc_430
        ic_400= ic_410 + ic_430
        qw_400.append({
            'oc_400': oc_400,
            'ic_400' :ic_400
        })
        oc_440 = oc_300 +oc_400
        ic_440 = ic_300 +ic_400
        qw_440.append({
            'oc_440':oc_440,
            'ic_440': ic_440
        })
        return {
                'doc_ids':data['ids'],
                'doc_model':data['model'],
                'start_date':start_date,
                'end_date':end_date,
                  'qw_100': qw_100,'qw_111': qw_111, 'qw_112': qw_112, 'qw_110': qw_110,
                 'qw_120':qw_120,'qw_121': qw_121, 'qw_122': qw_122, 'qw_123': qw_123, 'qw_130': qw_130, 'qw_131': qw_131, 'qw_132': qw_132, 'qw_133': qw_133, 'qw_134': qw_134, 'qw_135': qw_135, 'qw_136': qw_136, 'qw_137': qw_137, 'qw_139': qw_139,
                 'qw_140': qw_140,'qw_141': qw_141, 'qw_149': qw_149,
                 'qw_150': qw_150,'qw_151': qw_151, 'qw_152': qw_152, 'qw_153': qw_153, 'qw_154': qw_154, 'qw_155': qw_155,
                 'qw_200' :qw_200, 'qw_210':qw_210,'qw_211':qw_211,'qw_212':qw_212,'qw_213':qw_213,'qw_214':qw_214,'qw_215':qw_215,'qw_216':qw_216, 'qw_219' :qw_219, 'qw_220' :qw_220,
                  'qw_221': qw_221,'qw_222': qw_222, 'qw_223': qw_223, 'qw_224': qw_224, 'qw_225': qw_225, 'qw_226': qw_226, 'qw_227': qw_227, 'qw_228': qw_228, 'qw_229': qw_229, 'qw_230': qw_230, 'qw_231': qw_231, 'qw_232': qw_232, 'qw_240': qw_240, 'qw_241': qw_241, 'qw_242': qw_242,
                 'qw_250': qw_250,'qw_251': qw_251, 'qw_252': qw_252, 'qw_253': qw_253, 'qw_254': qw_254, 'qw_255': qw_255,
                 'qw_260': qw_260,'qw_261': qw_261, 'qw_262': qw_262, 'qw_263': qw_263, 'qw_268': qw_268,'qw_270': qw_270,
                 'qw_311':qw_311,'qw_312':qw_312,'qw_313':qw_313,'qw_314':qw_314,'qw_315':qw_315,'qw_316':qw_316,'qw_317':qw_317,'qw_318':qw_318,'qw_319':qw_319,'qw_320':qw_320,'qw_321':qw_321,'qw_322':qw_322,'qw_323':qw_323,'qw_324':qw_324,
                 'qw_331': qw_331, 'qw_332': qw_332, 'qw_333': qw_333, 'qw_334': qw_334, 'qw_335': qw_335, 'qw_336': qw_336, 'qw_337': qw_337, 'qw_338': qw_338, 'qw_339': qw_339, 'qw_340': qw_340, 'qw_341': qw_341, 'qw_342': qw_342, 'qw_343': qw_343,'qw_300': qw_300,'qw_310': qw_310,'qw_330': qw_330,
                 'qw_411a': qw_411a, 'qw_411b': qw_411b, 'qw_412': qw_412, 'qw_413': qw_413, 'qw_414': qw_414, 'qw_415': qw_415, 'qw_416': qw_416, 'qw_417': qw_417, 'qw_418': qw_418, 'qw_419': qw_419, 'qw_420': qw_420,
                 'qw_421a':qw_421a, 'qw_421b':qw_421b, 'qw_422':qw_422,'qw_431':qw_431,'qw_432':qw_432,
                 'qw_400':qw_400,'qw_410':qw_410,'qw_430':qw_430,'qw_411':qw_411,'qw_421':qw_421,'qw_440':qw_440,

                 
        }
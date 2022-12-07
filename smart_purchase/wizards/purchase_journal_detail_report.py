from odoo.exceptions import ValidationError
from odoo import models,fields,api, _
from datetime import datetime,time
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

class ReportPurchaseDetail(models.TransientModel):
    _name = 'purchase.detail.wizard'
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
        ],default='0'
    )

    report_type = fields.Selection(
        string ='Report type',
        selection= [
            (0,'Report by goods'),
            (1,'Report by vendors'),
            (2,'Report by employees')
        ], default = 0,required=True
    ) 
    
    def _get_default_products(self):
        products = self.env['product.template'].search([('active','=',True),('purchase_ok','=',True)])
        return  products

    def _get_default_vendors(self):
        return  self.env['res.partner'].search([('supplier','=',True)])

    def _get_default_employees(self):
        return  self.env['res.partner'].search([('partner_share','=',False)])

    def _get_default_category(self):
        _cate =  self.env['product.category'].search([('parent_id','=',False)])
        if _cate is not None:
            _cate = _cate[0] 
        return _cate

    filter_product_categories=fields.Many2one(string='Product categories',comodel_name='product.category', default = _get_default_category) 
    filter_vendors = fields.Many2many(string='Vendors',comodel_name ='res.partner',domain =[('supplier','=',True)],default=_get_default_vendors)
    filter_employees = fields.Many2many(string='Employees',comodel_name='res.partner', domain=[('partner_share','=',False)],default= _get_default_employees)
    filter_products = fields.Many2many(string='Products',  comodel_name='product.template',domain=[('active','=',True),('purchase_ok','=',True)], default= _get_default_products  )
 
    @api.onchange('filter_product_categories')
    def _default_so_tc(self):
        product_template = self.env['product.template']
        categ_id= int(self.filter_product_categories)
        if categ_id ==1 :
             products = product_template.search([])
        else :
             products = product_template.search([('categ_id', '=',categ_id)])
        self.filter_products= products


    # @api.onchange('report_type')
    # def _change_report_type(self):


    
    @staticmethod
    def to_number(str):
        number =0
        for value in str:
                try:
                    number =(int(value))
                except ValueError:
                    continue
        return number
    

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
        params = None
        if self.report_type == 0:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'products':self.filter_products,
            }
            return self.env.get('report.purchase.journal.detail.goods').reload_data(params)
            
        if self.report_type == 1:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'vendors':self.filter_vendors,
            }
            return self.env.get('report.purchase.journal.detail.vendors').reload_data(params)
           
        if self.report_type == 2:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'employees':self.filter_employees,
            }

            return self.env.get('report.purchase.journal.detail.employees').reload_data(params)

  

class GetJournalDetailView(models.AbstractModel):
    _name='report.smart_purchase.reportjournaldetail_display'
    
    @api.multi
    @api.model
    def _get_report_values(self,docids,data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= end_date + ' 23:59:59'
        filter_date = data['form']['filter_date']
        filter_product = data['form']['filter_product']
        product_ids= (tuple(self.to_array(filter_product)))
        docs=[]
        all_total=[]
        if len(product_ids) == 0 :
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
            self.env.cr.execute(
                """
                    select 
                    distinct
                    sp.date_done as accounting_date,
                    so.effective_date as effective_date,
                    so.name as name,
                    ai.date_invoice as write_date,
                    ai.invoice_number as num_id,
                    so.note as note, 
                    rp.barcode as id_vendor,
                    rp.name as vendor_name,
                    pp.default_code as default_code,
                    pt.name as product_name,
                    uu.name as uom_name,
                    sol.qty_delivered as qty_delivered,
                    sol.price_unit as price_unit,      
                    sol.price_subtotal as price_total,
                    sol.discount as discount
                    from purchase_order so
                    left join purchase_order_line sol
                    on so.id= sol.order_id
                    left join stock_picking sp
                    on so.id= sp.purchase_id
                    left join stock_move sm
                    on sol.id= sm.purchase_line_id
                    left join stock_move_line sml
                    on sml.picking_id= sp.id
                    left join account_move am
                    on sm.id= am.stock_move_id
                    left join account_invoice ai
                    on am.id = ai.move_id
                    left join res_partner rp 
                    on rp.id = so.partner_id
                    inner join product_product pp
                    on sol.product_id = pp.product_tmpl_id
                    inner join product_template pt 
                    on pt.id= pp.product_tmpl_id
                    inner join uom_uom uu
                    on sol.product_uom= uu.id
                    where sol.product_id in %s
                    and  sml.date >= %s and sml.date <= %s and sp.state='done'

                """,
                (product_ids,start_date, end_date)
            )
        self.purchase_order = self.env.cr.fetchall() 
        if filter_product is False:
            pass
        else:
            list_record = []
            all_qty_delivered = 0
            all_price_total = 0
            all_discount = 0
            all_price_unit = 0
            for item in self.purchase_order:
                        docs.append({
                            'create_date':item[0],
                            'write_date':item[1],
                            'name':item[2],
                            'order_date':item[3],
                            'num_id':item[4],
                            'note':item[5],
                            'id_vendor':item[6],
                            'name_vendor':item[7],
                            'id_product':item[8],
                            'name_product':item[9],
                            'uom_uom':item[10],
                            'qty_delivered':item[11],
                            'price_unit':item[12],
                            'price_total':item[13],
                            'discount':item[14],
                        })
                        if item[13] is None : all_price_total += all_price_total
                        else:
                            all_price_total += int(item[13])

                        if item[11] is None :    all_qty_delivered +=all_qty_delivered
                        else:
                            all_qty_delivered += int(item[11])
                        if item[14] is None : all_discount +=all_discount
                        else:
                            all_discount += int(item[14])
                        if item[12] is None : all_price_unit += all_price_unit
                        else:
                            all_price_unit += int(item[12])
            all_total.append({
                'all_qty_delivered':all_qty_delivered,
                'all_price_total':all_price_total,
                'all_discount':all_discount,
                'all_price_unit':all_price_unit,
            })
        return{
            'doc_ids':data['ids'],
            'doc_model':data['model'],
            'start_date':start_date,
            'end_date':end_date,
            'docs':docs,
            'all_total':all_total,
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


from odoo import api,models,fields,osv
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

class ReportSaleGeneral(models.TransientModel):
    _name = 'sale.general.wizard'
   
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

    report_type = fields.Selection(
        string ='Report type',
        selection= [
            (0,'Report by goods'),
            (1,'Report by customers'),
            (2,'Report by employees')
        ], default = 0
    ) 

    def _get_default_products(self):
        products = self.env['product.template'].search([('active','=',True),('sale_ok','=',True)]).ids
        return  products

    def _get_default_customers(self):
        return  self.env['res.partner'].search([('customer','=',True)]).ids

    def _get_default_employees(self):
        return  self.env['res.partner'].search([('partner_share','=',False)]).ids

    def _get_default_category(self):
        _cate =  self.env['product.category'].search([('parent_id','=',False)])
        if _cate is not None:
            _cate = _cate[0] 
        return _cate

    filter_product_categories=fields.Many2one(string='Product categories',comodel_name='product.category', default = _get_default_category) 
    filter_customers = fields.Many2many(string='Customers',comodel_name ='res.partner',domain =[('customer','=',True)],default=_get_default_customers)
    filter_employees = fields.Many2many(string='Employees',comodel_name='res.partner', domain=[('partner_share','=',False)],default= _get_default_employees)
    filter_products = fields.Many2many(string='Products',  comodel_name='product.template',domain=[('active','=',True),('sale_ok','=',True)], default= _get_default_products  )
 
    @api.onchange('filter_product_categories')
    def _default_so_tc(self):
        product_template = self.env['product.template']
        categ_id= int(self.filter_product_categories)
        if categ_id ==1 :
             products = product_template.search([])
        else :
             products = product_template.search([('categ_id', '=',categ_id)])
        self.filter_products= products
 
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
 
    
    @api.multi
    def get_info (self):
        data ={
            'ids': self.ids,
            'model': self._name,
            'form': {
                'filter_date' :self.filter_date,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'filter_product':self.filter_product,
            },
        }
        return self.env.ref('smart_sale.reportgeneral').report_action(self, data=data)


    def set_params_to_list(self):  
        params = None
        if self.report_type == 0:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'products':self.filter_products,
            }
            return self.env.get('report.sale.general.goods').reload_data(params)
            
        if self.report_type == 1:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'customers':self.filter_customers,
            }
            return self.env.get('report.sale.general.customers').reload_data(params)
           
        if self.report_type == 2:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'employees':self.filter_employees,
            }

            return self.env.get('report.sale.general.employees').reload_data(params)

  
class GetSaleGeneral(models.AbstractModel):
    _name='report.smart_sale.reportgeneral_display'

    @api.model
    def _get_report_values(self,docids,data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= end_date + ' 23:59:59'
        filter_date=data['form']['filter_date']
        filter_product=data['form']['filter_product']

        docs=[]
        all_total=[]
        
        # product_id_query= self.env['sale.order.line'].search([()])
        if filter_product is False:
            pass
        else:
            length = len(filter_product) -1
            list_record = []
            all_qty_delivered = 0
            all_price_total = 0
            all_discount = 0

            for record in filter_product[17:length].split(","):
                if record.strip().isdigit() == True:
                    list_record.append(record.strip())
            tuple_record = tuple(list_record)
            self.env.cr.execute(
                """
                    select 
                    MAX(sol.name) as name,
                    MAX(pp.default_code) as code,
                    MAX(pt.name) as product_name,
                    MAX(uu.name) as unit,
                    sum(sol.qty_delivered) as all_qty_delivered,
                    sum(sol.price_subtotal) as all_price_total,
                    sum(sol.discount) as all_discount 
                    from sale_order so
                    left join sale_order_line sol
                    on so.id= sol.order_id
                    left join product_product pp
                    on sol.product_id = pp.product_tmpl_id
                    left join product_template pt 
                    on pt.id= pp.product_tmpl_id
                    left join uom_uom uu
                    on sol.product_uom= uu.id
                    left join stock_move sm 
                    on sm.sale_line_id= sol.id
                    left join stock_picking sp
                    on sm.picking_id = sp.id
                    left join stock_move_line sml
                    on sm.id = sml.move_id
                    where sol.product_id in %s and sml.date >= %s and sml.date <= %s 
                    group by pt.id
                        """
                        ,(tuple_record,start_date, end_date)
                    )
            self.sale_order = self.env.cr.fetchall() 
            
            docs = []
            for record in self.sale_order:
                docs.append({
                    'id_product':record[1],
                    'name_product':record[2],
                    'uom_uom':record[3],
                    'qty_delivered':record[4],
                    'price_total':record[5],
                    'discount':record[6],
                })
                all_price_total += int(record[5])
                all_qty_delivered += int(record[4])
                all_discount += int(record[6])
            
            
            all_total.append({
                'all_qty_delivered':all_qty_delivered,
                'all_price_total':all_price_total,
                'all_discount':all_discount,
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
             
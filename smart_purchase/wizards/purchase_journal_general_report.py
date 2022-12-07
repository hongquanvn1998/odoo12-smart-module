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
class PurchaseJournalGeneralWizard(models.TransientModel) :
    _name= 'purchase.journal.general.wizard' 
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
            (1,'Report by vendors'),
            (2,'Report by employees')
        ], default = 0, required=True
    ) 

    def _get_default_products(self):
        products = self.env['product.template'].search([('active','=',True),('sale_ok','=',True)])
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
    filter_vendors = fields.Many2many(string='Customers',comodel_name ='res.partner',domain =[('supplier','=',True)],default=_get_default_vendors)
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
 
     
    def set_params_to_list(self):  
        params = None
        if self.report_type == 0:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'products':self.filter_products,
            }
            return self.env.get('report.purchase.general.goods').reload_data(params)
            
        if self.report_type == 1:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'vendors':self.filter_vendors,
            }
            return self.env.get('report.purchase.general.vendors').reload_data(params)
           
        if self.report_type == 2:
            params = {
                'report_type': self.report_type,
                'start_date':self.start_date,
                'end_date': self.end_date,
                'employees':self.filter_employees,
            }

            return self.env.get('report.purchase.general.employees').reload_data(params)

    # @api.multi
    # def get_report (self):
    #     data ={
    #         'ids': self.ids,
    #         'model': self._name,
    #         'form': {
    #              'filter_date' :self.filter_date,
    #              'date_start': self.date_start,
    #              'date_end': self.date_end,
    #              'filter_product' : self.filter_product
    #         },
    #     }
    #     return self.env.ref('smart_purchase.purchase_journal_general_report').report_action(self, data=data)



class PurchaseJournalGeneralGetView(models.AbstractModel):
    _name = 'report.smart_purchase.purchase_journal_general_report_display'
    

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
        pt.id,
		MAX(pl.name),
        MAX(pp.default_code) as default_code,
        MAX(uu.name) as uom_name,
        sum(qty_received) as product_uom_qty,
        sum(price_subtotal) as price_subtotal,
        sum(price_tax) as price_tax,
        sum(qty_received) as amount_returned,
        sum(qty_invoiced) as return_value, 
        sum(price_total) as price_total
        from purchase_order_line pl
        inner join product_product pp
        on pl.product_id = pp.product_tmpl_id
        inner join product_template pt 
        on pt.id= pp.product_tmpl_id
        inner join uom_uom uu
        on pl.product_uom= uu.id
        left join stock_move sm 
        on sm.purchase_line_id= pl.id
        left join stock_picking sp
        on sm.picking_id = sp.id
		left join stock_move_line sml
        on sm.id = sml.move_id
        where pl.product_id in %s
        and  sml.date >= %s and sml.date <= %s  and  sp.state='done'
        group by (pt.id)
                """
                ,(product_ids,date_start, date_end)
            )
        self.purchase_order = self.env.cr.fetchall() 
        docs = []
        sum_product_uom_qty= 0
        sum_price_subtotal =0
        sum_price_tax= 0
        sum_amount_returned=0
        sum_return_value=0
        sum_price_total = 0

        for item in self.purchase_order:
            if item[4] is None  :
                sum_product_uom_qty += sum_product_uom_qty
            else:
                sum_product_uom_qty += item[4]    
            if item[5] is None  : 
                sum_price_subtotal += sum_price_subtotal 
            else:
               sum_price_subtotal += item[5]  
            if item[6] is None  : 
               sum_price_tax += sum_price_tax
            else :
               sum_price_tax +=  item[6]

            if item[7] is None  : 
               sum_amount_returned += sum_amount_returned
            else :
               sum_amount_returned +=  item[7]
            if item[8] is None  : 
                sum_return_value += sum_return_value
            else :
                sum_return_value +=   item[8]
            if item[9] is None  : 
                sum_price_total += sum_price_total
            else :
                sum_price_total +=  item[9]
            docs.append({
                    'name': item[1],
                    'default_code': item[2],
                    'unit' : item[3],
                    'product_uom_qty':  item[4],
                    'price_subtotal': item[5],
                    'price_tax': item[6],
                    'amount_returned':item[7],
                    'return_value': item[8],
                    'price_total': item[9],
                })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'sum_product_uom_qty' :sum_product_uom_qty,
            'sum_price_subtotal' :sum_price_subtotal,
            'sum_price_tax' :sum_price_tax,
            'sum_amount_returned' :sum_amount_returned,
            'sum_return_value' :sum_return_value,
            'sum_price_total' :sum_price_total,
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

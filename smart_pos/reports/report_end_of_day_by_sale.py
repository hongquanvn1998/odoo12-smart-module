from odoo import models,fields,api,tools
from datetime import datetime
class ReportEndOfDayBySale(models.Model):
    _name = 'report.end.of.day.by.sale'
    _auto = False
    id = fields.Integer(string='ID')
    order_id = fields.Integer(string='Order ID') 
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')
    qty_total= fields.Integer(string='Quantity')
    amount_total= fields.Float(string='Amount Total')
    amount_paid = fields.Float(string='Amount Paid')
    partner_name = fields.Char(string='Partner')
    seller_name =  fields.Char(string='Seller')
    counter_name = fields.Char(string='Counter Name')
    # goods_name = fields.Char(string='Name')
    # sale_quantity = fields.Integer(string='Quantity')
    # revenue = fields.Float(string='Revenue')
    # return_quantity=fields.Integer(string='Return quantity')
    # return_price=fields.Float(string='Return price')
    # real_income = fields.Float(string='Real income')

    def reload_data(self,*kw):
        # product_list = kw[0].get('filter_product',None)
        start_date = kw[0].get('start_date')
        # filter_types=kw[0].get('filter_types')
        filter_partner=kw[0].get('filter_partner')
        filter_employee=kw[0].get('filter_employee')
        filter_method_payment=kw[0].get('filter_method_payment')
        employee_items = tuple(filter_employee.ids)
        partner_items = tuple(filter_partner.ids)


        # SELECT  ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, po.code,po.amount_total,po.qty_total, po.discount_percent,po.amount_paid, po.amount_return, po.date_order date,
        #     rp.name partner_name,
        #     (select (_rp.name) from res_users _ru inner join res_partner _rp
        #     on _ru.partner_id = _rp.id
        #     where _ru.id =po.seller_id ) seller_name

        #     FROM pos_order po
        #          inner join res_partner rp on po.partner_id = rp.id
        
        sql = """
            CREATE OR REPLACE VIEW  %s AS           
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            po.id order_id,
            po.code,
            po.amount_total,
            po.qty_total, 
            po.discount_percent,
            po.amount_paid, 
            po.amount_return, 
            po.date_order date,
            rp.name partner_name,
            pc.name  counter_name,
            (select (_rp.name) 
            from  res_users _ru left join res_partner _rp  on _ru.partner_id = _rp.id
            where _ru.id =po.seller_id ) seller_name

            FROM pos_order po 
                 left join res_partner rp on po.partner_id = rp.id
                 left join pos_counter pc on pc.id= po.counter_id
            WHERE 
            po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59' 
             """ %(self._table,start_date, start_date)

        if  len(employee_items) >0:
            sql+= """ 
             AND po.seller_id = %s        
        """  % employee_items[0]
        if len(partner_items) >0:
            sql+= """
             AND po.partner_id = %s 

            """ %  partner_items[0]
        # sql+= """"""%(self._table)
        if 'vi_VN' in self._context.values():
                name = 'Báo cáo cuối ngày'
        else:
            name = 'Report end of day'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.end.of.day.by.sale' ,
            "context":{'start_date':start_date }
                }

    def detail(self):       
        _id = self.order_id or None
        if _id is None:
            raise ValidationError('Object not exits!')
        return { 
                'name': 'Chi tiết đơn hàng ' +  self.code,
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": 'pos.order',                
                # 'res_code':_code
                 'res_id':_id,
                 'nodestroy': True,
                 'target': 'new',                 
                 'flags': {'mode': 'readonly'}
                }   
  
    #"context":{'start_date':start_date, 'search_default_code': 1 }
    # _name = 'report.end.of.day.by.sale'
    # _auto = False
    # id = fields.Integer(string='ID')
    # code_exchange = fields.Char(string='Code')
    # date = fields.Datetime(string='Date')
    # quantity = fields.Integer(string='Quantity')
    # revenue = fields.Float(string='Revenue')
    # other_revenues = fields.Float(string='Other revenues')
    # return_expenses = fields.Float(string='Return expenses')
    # payment = fields.Float(string='Real income')

    # def reload_data(self,*kw):
    #     start_date =''
    #     end_date = ''
    #     product_list = kw[0].get('filter_product',None)
    #     start_date = kw[0].get('start_date')
    #     filter_types=kw[0].get('filter_types')
    #     filter_partner=kw[0].get('filter_partner')
    #     filter_employee=kw[0].get('filter_employee')
    #     filter_method_payment=kw[0].get('filter_method_payment')
    #     employee_items = tuple(filter_employee.ids)
    #     partner_items = tuple(filter_partner.ids)
        
    #     sql = """
    #         CREATE OR REPLACE VIEW  %s AS
    #         select 
    #        *
    #         from
    #     """ %( self._table,)

    #     tools.drop_view_if_exists(self._cr, '%s' % self._table) 
    #     self.env.cr.execute(sql)
    #     return { 
    #         'name': self._table,
    #         "type": "ir.actions.act_window",
    #         "view_mode": "tree",
    #         "res_model": 'report.end.of.day.by.sale' ,
    #         "context":{'start_date':start_date,'end_date':end_date}
    #             }
  

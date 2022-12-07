from odoo import models,fields,api,tools
from datetime import datetime
class ReportEndOfDayByGoods(models.Model):
    _name = 'report.end.of.day.by.goods'
    _auto = False
    id = fields.Integer(string='ID')
    order_id = fields.Integer(string='Order ID') 
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')
    quantity= fields.Integer(string='Quantity')
    amount_total= fields.Float(string='Amount Total')
    amount_paid = fields.Float(string='Amount Paid')
    product_name = fields.Char(string='Product Name')
    product_code = fields.Char(string='Product Code')
    counter_name = fields.Char(string='Counter Name')
    # stt = fields.Integer(string='STT')
    # partner_name = fields.Char(string='Partner')
    # seller_name =  fields.Char(string='Seller')
    # goods_name = fields.Char(string='Name')
    # sale_quantity = fields.Integer(string='Quantity')
    # revenue = fields.Float(string='Revenue')
    # return_quantity=fields.Integer(string='Return quantity')
    # return_price=fields.Float(string='Return price')
    # real_income = fields.Float(string='Real income')

    def reload_data(self,*kw):
        # product_list = kw[0].get('filter_product',None)
        start_date = kw[0].get('start_date')
        filter_types=kw[0].get('filter_types')
        filter_partner=kw[0].get('filter_partner')
        filter_employee=kw[0].get('filter_employee')
        filter_method_payment=kw[0].get('filter_method_payment')
        employee_items = tuple(filter_employee.ids)
        partner_items = tuple(filter_partner.ids)
        
        

        sql = """
            CREATE OR REPLACE VIEW  %s AS         
                       
            SELECT
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
            po.id order_id,
            po.amount_paid,
            pt.default_code product_code,
            pt.name product_name,
            pol.quantity quantity,
            pol.price_subtotal amount_total,
            po.code code,
            po.date_order date,
            pc.name  counter_name
            FROM 

            pos_order_line pol 
            
            left join product_product pp on pp.id = pol.product_id
            left join product_template pt on pt.id = pp.product_tmpl_id
            left join pos_order po on po.id = pol.order_id
            left join pos_counter pc on pc.id= po.counter_id

            WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59'
            ORDER BY po.date_order ASC

             

             """ %(self._table,start_date, start_date)

        # if  len(employee_items) >0:
        #     sql+= """ 
        #      AND po.seller_id = %s        
        # """  % employee_items[0]
        # if len(partner_items) >0:
        #     sql+= """
        #      AND po.partner_id = %s 

        #     """ %  partner_items[0]
      
        if 'vi_VN' in self._context.values():
                name = 'Báo cáo cuối ngày theo hàng hóa'
        else:
            name = 'Report end of day by good'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.end.of.day.by.goods' ,
            "context":{'start_date':start_date  }
            
            }

    def reload_data_mobile(self,**kw):
        # product_list = kw[0].get('filter_product',None)
        start_date = kw.get('start_date')
        is_admin = kw.get('is_admin')
        top_quantity = kw.get('top_quantity')
        limit = kw.get('limit')

        data_output = []
        create_uid = "and po.create_uid = %s"%self.env.uid if is_admin == False else ""
        quantity_or_amount = "ORDER BY quantity DESC" if top_quantity == True else "ORDER BY amount_total DESC"
        limit_10 = "LIMIT 10" if limit == True else ""
        


        sql = """
            SELECT
            pp.id,
            pt.default_code product_code,
            pt.name product_name,
            Sum(pol.quantity) quantity,
            Sum(pol.price_subtotal) amount_total
            FROM 

            pos_order_line pol 
            
            left join product_product pp on pp.id = pol.product_id
            left join product_template pt on pt.id = pp.product_tmpl_id
            left join pos_order po on po.id = pol.order_id

            WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59' %s
            GROUP BY pp.id,product_code,product_name
            %s
            %s
             

             """ %(start_date, start_date,create_uid,quantity_or_amount,limit_10)
        
        self.env.cr.execute(sql)
        data = self.env.cr.fetchall()
        for i in data:
            list_data = {
                'id':i[0],
                'product_name':i[2] or False,
                'total_amount':i[4] or False,
                'total_product':i[3] or False,
                'product_code':i[1] or False,
            }
            data_output.append(list_data)
        return data_output

    def reload_dashboard_data_mobile(self,**kw):
        start_date = kw.get('start_date')
        is_admin = kw.get('is_admin')
        add_product = []
        data_output = {}

        create_uid = "and po.create_uid = %s"%self.env.uid if is_admin == False else ""
        
        sql_total_quantity = """
            SELECT
            sum(pol.quantity) quantity

            FROM 

            pos_order_line pol 
            left join pos_order po on po.id = pol.order_id

            WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59'
             """ %(start_date, start_date)
        self.env.cr.execute(sql_total_quantity)
        data_total_quantity = self.env.cr.fetchall()
        data_output['total_quantity'] = data_total_quantity[0][0]

        sql = """
            SELECT
            pt.name product_name,
            sum(pol.quantity) quantity
            FROM 

            pos_order_line pol 
            
            left join product_product pp on pp.id = pol.product_id
            left join product_template pt on pt.id = pp.product_tmpl_id
            left join pos_order po on po.id = pol.order_id
            left join pos_counter pc on pc.id= po.counter_id

            WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59' %s
            GROUP BY pt.name
            ORDER BY quantity DESC
            LIMIT 3

             

             """ %(start_date, start_date,create_uid)
        
        self.env.cr.execute(sql)
        data = self.env.cr.fetchall()
        for i in data:
            list_data = {
                'product_name':i[0] or False,
                'total_product':i[1] or False,
            }
            add_product.append(list_data)
        data_output['product'] = add_product

        return data_output

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

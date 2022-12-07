from odoo import models,fields,api,tools
from datetime import datetime
class ReportSaleByTime(models.Model):
    _name = 'report.sale.by.time'
    _auto = False
 
    id = fields.Integer(string='ID')
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')
    quantity = fields.Integer(string='Quantity')
    amount_total= fields.Float(string='Amount Total')
    amount_paid = fields.Float(string='Amount Paid')
    partner_name = fields.Char(string='Partner')
    seller_name =  fields.Char(string='Seller')
    counter_name = fields.Char(string='Counter Name')


    def reload_data(self,*kw):
        start_date = kw[0].get('start_date')
        end_date = kw[0].get('end_date')
        # filter_employee=kw[0].get('filter_employee')
        # filter_method_payment=kw[0].get('filter_method_payment')
        # employee_items = tuple(filter_employee.ids)
        # partner_items = tuple(filter_partner.ids)

        sql = """
            CREATE OR REPLACE VIEW  %s AS           
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            po.code,
            po.amount_total,
            po.qty_total quantity, 
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
             """ %(self._table,start_date, end_date)

        # if  len(employee_items) >0:
        #     sql+= """ 
        #      AND po.seller_id = %s        
        # """  % employee_items[0]
       
        # sql+= """"""%(self._table)
        if 'vi_VN' in self._context.values():
                name = 'Báo cáo bán hàng theo thời gian'
        else:
            name = 'Report sale by time'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.by.time' ,
            "context":{'start_date':start_date,'end_date':end_date}

            
                }
    def reload_data_mobile(self,**kw):
        start_date = kw.get('start_date')
        end_date = kw.get('end_date')
        is_admin = kw.get('is_admin')

        data_output = []

        create_uid = "and po.create_uid = %s"%self.env.uid if is_admin == False else ""


        sql = """     
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            po.id,
            po.code,
            po.amount_total,
            po.qty_total quantity, 
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
            po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59' %s
             """ %(start_date, end_date,create_uid)

        self.env.cr.execute(sql)
        data = self.env.cr.fetchall()
        for i in data:
            list_data = {
                'id':i[1],
                'bill':i[2] or False,
                'customer_name': i[9] or False,
                'date_time':i[8] or False,
                'total_product':i[4] or False,
                'total_bill':i[3] or False,
                'counter_name':i[10] or False,
                'seller_name':i[11] or False
            }
            data_output.append(list_data)
        return data_output
    
    def reload_sale_data_mobile(self,**kw):
        start_date = kw.get('start_date')
        end_date = kw.get('end_date')
        data_output = []

        time_delta = datetime.strptime(end_date,'%Y-%m-%d') - datetime.strptime(start_date,'%Y-%m-%d')

        if time_delta.days > 31:
            day_or_year = 'extract(year from date_order)::int'

        else:
            day_or_year = 'extract(day from date_order)::int'


        sql = """     
            SELECT 
            COUNT(po.id),
            extract(month from date_order)::int,
            %s

            FROM pos_order po 
            WHERE 
            po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59' 
            GROUP BY 2,3
            ORDER BY 2,3 ASC
             """ %(day_or_year,start_date, end_date)

        self.env.cr.execute(sql)
        data = self.env.cr.fetchall()
        if time_delta.days > 31:
            for i in data:
                dict_data = {
                    'bill_count':i[0],
                    'month':i[1],
                    'year':i[2]
                }
                data_output.append(dict_data)
        else:
            for i in data:
                dict_data = {
                    'bill_count':i[0],
                    'month':i[1],
                    'day':i[2]
                }
                data_output.append(dict_data)
        return data_output
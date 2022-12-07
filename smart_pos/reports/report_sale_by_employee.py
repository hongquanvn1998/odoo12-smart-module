from odoo import models,fields,api,tools
from datetime import datetime
class ReportSaleByEmployee(models.Model):
    _name = 'report.sale.by.employee'
    _auto = False
    id = fields.Integer(string='ID')
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')    
    amount_total= fields.Float(string='Amount Total')
    # partner_id = fields.Many2one('res.partner', string='Partner')
    seller_name = fields.Char(string='Seller Name')
    # employee = fields.Char(string='Name')
    # revenue = fields.Float(string='Revenue')
    # return_price=fields.Float(string='Return price')
    # real_income = fields.Float(string='Real income')


    def reload_data(self,*kw):
        start_date = kw[0].get('start_date')
        end_date = kw[0].get('end_date')
        filter_employee=kw[0].get('filter_employee')
        if filter_employee is not None:
            employee_items = tuple(filter_employee.ids)
        # filter_pricelist=kw[0].get('filter_pricelist')
        # pricelist_items = tuple(filter_pricelist.ids)
        
        sql = """
            CREATE OR REPLACE VIEW  %s AS
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            po.code,
            po.amount_total,
            po.qty_total, 
            po.discount_percent,
            po.amount_paid, 
            po.amount_return, 
            po.date_order date,
            po.partner_id,
            (select (_rp.name) 
            from  res_users _ru left join res_partner _rp  on _ru.partner_id = _rp.id
            where _ru.id =po.seller_id ) seller_name

            FROM pos_order po

            WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59'

           
        """ %( self._table,start_date, end_date)
        
        if filter_employee is not None and  len(employee_items) >0: 
            sql+= """ 
             AND po.seller_id = %s        
        """  % employee_items[0]
       
        sql+= """ 
        ORDER BY po.date_order ASC
         """ 


       
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': 'Báo cáo bán hàng theo nhân viên',
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.by.employee' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
    
    def reload_sale_data_mobile(self, **kw):
        start_date = kw.get('start_date')
        end_date = kw.get('end_date')
        detail = kw.get('detail')
        data_output_sellers =[]
        data_sellers_total_amount = 0
        data_output_sellers.append(data_sellers_total_amount)

        limit_row = "LIMIT 3" if detail==0 else ''

        sql_sellers = """
            SELECT 
            Sum(po.amount_total) total_amount,
            (select (_rp.name) 
            from  res_users _ru left join res_partner _rp  on _ru.partner_id = _rp.id
            where _ru.id =po.seller_id ) seller_name

            FROM pos_order po

            WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59'
            GROUP BY seller_name
            ORDER BY total_amount DESC 
            %s
           
        """ %(start_date, end_date,limit_row)
        self.env.cr.execute(sql_sellers)
        data_sellers = self.env.cr.fetchall()

        for s in data_sellers:
            dict_data_sellers = {
                'name':s[1],
                'total_amount':s[0]
            }
            data_output_sellers[0] += s[0]
            data_output_sellers.append(dict_data_sellers)

        return data_output_sellers
  

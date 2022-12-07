from odoo import models,fields,api,tools
from datetime import datetime
from odoo.addons import decimal_precision as dp
class ReportSaleByProfit(models.Model):
    _name = 'report.pos.revenue'
    _auto = False
    id = fields.Integer(string='ID')    
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')
    total_quantity = fields.Integer(string='Total_quantity')
    
    # total_goods = fields.Float(string='Total goods')
    # discount = fields.Float(string='Discount')
    revenue = fields.Float(string='Revenue')
    total_profit=fields.Float(string='Total profit')
    # amount_fix = fields.Float(string='Total cost price', digits=dp.get_precision('total_cost_price'))
    # total_profit = fields.float('Total profit', help="Base price to compute the customer price. Sometimes called the catalog price.", digits=dp.get_precision('total_profit'))
    # total_profit = fields.Float(digits=(3,3),  digits_compute=dp.get_precision('Total profit'))


    def reload_data(self,*kw):
        print(kw)
        start_date = kw[0].get('start_date')
        end_date = kw[0].get('end_date')
       
        sql = """
            CREATE OR REPLACE VIEW  %s AS
            SELECT
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
            code code,  
            qty_total total_quantity,          
            amount_total total_profit,
            discount discount,
            discount_percent revenue,
            amount_paid amount_fix,
            amount_return,
            date_order date
            FROM pos_order 

            WHERE date_order >= '%s 00:00:00' and date_order <= '%s 23:59:59'

        """ %  (self._table,start_date, end_date)
        # (self._table)

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
      
        self.env.cr.execute(sql)
        return { 
            'name': 'Báo cáo doanh thu',
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.pos.revenue' ,
            "context":{'start_date':start_date,'end_date':end_date, 'search_default_date': 1 }
                }

    def reload_sale_data_mobile(self,**kw):
        start_date = kw.get('start_date')
        end_date = kw.get('end_date')
        data_output_revenue =[]
        day_or_year_revenue = ''

        time_delta = datetime.strptime(end_date,'%Y-%m-%d') - datetime.strptime(start_date,'%Y-%m-%d')

        if time_delta.days > 31:
            day_or_year_revenue = 'extract(year from date_order)::int,'
        else:
            day_or_year_revenue = 'extract(day from date_order)::int AS day,'

        sql_revenue = """
            SELECT   
            extract(month from date_order)::int AS month,
            %s
            sum(amount_total) as total_profit,
            sum(qty_total) total_quantity
            FROM pos_order 

            WHERE date_order >= '%s 00:00:00' and date_order <= '%s 23:59:59'
            GROUP BY 1,2
            ORDER BY 1,2 ASC
        """ %  (day_or_year_revenue,start_date, end_date)

        self.env.cr.execute(sql_revenue)
        data_revenue = self.env.cr.fetchall()

        if time_delta.days > 31:
            for i in data_revenue:
                dict_data_revenue = {
                    'amount_total':i[2],
                    'month':i[0],
                    'year':i[1],
                    'total_quantity':i[3]
                }
                data_output_revenue.append(dict_data_revenue)
        else:
            for i in data_revenue:
                dict_data_revenue = {
                    'amount_total':i[2],
                    'month':i[0],
                    'day':i[1],
                    'total_quantity':i[3]
                }
                data_output_revenue.append(dict_data_revenue)

        return data_output_revenue
    
    def reload_dashboard_data_mobile(self,**kw):
        start_date = kw.get('start_date')
        is_admin = kw.get('is_admin')

        data_output_revenue =[]

        create_uid = "and create_uid = %s"%self.env.uid if is_admin == False else ""

        sql_revenue = """
            SELECT   
            TIMESTAMP WITH TIME ZONE 'epoch' +
            INTERVAL '1 second' * round(extract('epoch' from date_order) / 3600) * 3600 as timestamp,
            sum(amount_total) as total_profit
            FROM pos_order 

            WHERE date_order >= '%s 00:00:00' and date_order <= '%s 23:59:59' %s
            GROUP BY 
            round(extract('epoch' from date_order) / 3600)
            ORDER BY timestamp ASC
        """ %  (start_date,start_date,create_uid)

        self.env.cr.execute(sql_revenue)
        data_revenue = self.env.cr.fetchall()
        
        for i in data_revenue:
            dict_data_revenue = {
                'amount_total':i[1],
                'hour':i[0].hour
            }
            data_output_revenue.append(dict_data_revenue)

        return data_output_revenue
      
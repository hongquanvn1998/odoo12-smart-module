from odoo import models,fields,api,tools
from datetime import datetime
class ReportSaleByProfit(models.Model):
    _name = 'report.sale.by.profit'
    _auto = False
    id = fields.Integer(string='ID')
    sold_quantity = fields.Integer(string='Sold Quantity')
    profit_rate = fields.Float(string='Profit Rate')
    profit = fields.Float(string='Profit')
    # amount_paid = fields.Float(string='Amount Paid')
    product_name = fields.Char(string='Product Name')   
    counter_name = fields.Char(string='Counter Name')  
   
    def reload_data(self,*kw):
        start_date = kw[0].get('start_date')
        end_date = kw[0].get('end_date')       
        # filter_goods=kw[0].get('filter_goods')
        # filter_goods_category=kw[0].get('filter_goods_category')
        # user_items = tuple(filter_goods.ids)
        # partner_items = tuple(partner_items.ids)
        
        sql = """
            CREATE OR REPLACE VIEW  %s AS

           SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,  
            pt.name as product_name,
            pc.name as counter_name,
            sum( abs(sv.value)) as cost,
            sum(sv.product_qty) as sold_quantity,
            sum(pol.price_subtotal) as total_amount,
            (sum(pol.price_subtotal) - sum(abs(sv.value))) as profit ,
            round(((sum(pol.price_subtotal) -  sum(abs(sv.value)))/sum(pol.price_subtotal)) * 100)  as profit_rate

            FROM 
                            stock_move sv  
                            left join product_product pp on sv.product_id = pp.id
                            left join product_template pt on pt.id = pp.product_tmpl_id
                            left join pos_order_line pol on  sv.order_line_id = pol.id
                            left join pos_order po on pol.order_id = po.id
                            left join pos_counter  pc on po.counter_id = pc.id
                            
            WHERE sv.order_line_id >0

                 AND pol.create_date >= '%s 00:00:00' 
                 AND pol.create_date <= '%s 23:59:59' 

            GROUP BY   pt.name, pc.name 
             """ %(self._table, start_date, end_date)

        if 'vi_VN' in self._context.values():
                name = 'Báo cáo lợi nhuận'
        else:
            name = 'Report Sale Profit'

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.by.profit' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
    def reload_sale_data_mobile(self, **kw):
        start_date = kw.get('start_date')
        end_date = kw.get('end_date')
        data_output_profit =[]
        day_or_year_profit = ''

        time_delta = datetime.strptime(end_date,'%Y-%m-%d') - datetime.strptime(start_date,'%Y-%m-%d')

        if time_delta.days > 31:
            day_or_year_profit = 'extract(year from pol.create_date)::int'

        else:
            day_or_year_profit = 'extract(day from pol.create_date)::int AS day'


        # left join product_product pp on sv.product_id = pp.id
        # left join product_template pt on pt.id = pp.product_tmpl_id
        sql_profit = """
           SELECT
            sum( abs(sv.value)) as cost,
            sum(pol.price_subtotal) as total_amount,
            (sum(pol.price_subtotal) - sum(abs(sv.value))) as profit,
            extract(month from pol.create_date)::int AS month,
            %s

            FROM 
                            stock_move sv  
                            left join pos_order_line pol on  sv.order_line_id = pol.id
                            left join pos_order po on pol.order_id = po.id
                            
            WHERE sv.order_line_id >0

                 AND pol.create_date >= '%s 00:00:00' 
                 AND pol.create_date <= '%s 23:59:59'
            GROUP BY 4,5
            ORDER BY 4,5
             """ %(day_or_year_profit,start_date, end_date)
        self.env.cr.execute(sql_profit)
        data_profit = self.env.cr.fetchall()

        if time_delta.days > 31:
            for e in data_profit:
                dict_data_profit = {
                    'cost':e[0],
                    'total_amount':e[1],
                    'profit':e[2],
                    'month':e[3],
                    'year':e[4]
                }
                data_output_profit.append(dict_data_profit)
        else:
            for e in data_profit:
                dict_data_profit = {
                    'cost':e[0],
                    'total_amount':e[1],
                    'profit':e[2],
                    'month':e[3],
                    'day':e[4]
                }
                data_output_profit.append(dict_data_profit)
                
        return data_output_profit

  





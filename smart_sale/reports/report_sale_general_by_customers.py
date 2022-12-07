from odoo import models, fields, api, tools
import datetime

class ReportSaleGeneralCustomer(models.Model):
    _name ='report.sale.general.customers'
    _auto = False
    _order = "customer_name asc"

    id = fields.Integer(string='ID')
    customer_code = fields.Char(string='Customer code')
    customer_name = fields.Char(string='Customer name')
    gross_revenue = fields.Float(string='Gross revenue')
    discount = fields.Float(string='Discount')
    return_quantity = fields.Float(string='Return quantity')
    return_value = fields.Float(string='Value of return') 
    net_revenue = fields.Float('Net revenue')
    province = fields.Char(string='Province/City')
    district = fields.Char(string='District')
    
    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        customers = kw[0].get('customers',None)
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        customer_items = tuple(customers.ids)
        if len(customer_items)<=1:
            customer_items = customer_items + tuple('0')+tuple('0')

        sql = """
             CREATE OR REPLACE VIEW %s AS
            select 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
            rp.barcode customer_code,
            rp.NAME customer_name,
            sum(sol.product_uom_qty*sol.price_unit) gross_revenue ,
            sum(sol.product_uom_qty*sol.price_unit*sol.discount/100) discount,
            0 return_quantity,
            0 return_value,
            sum(sol.price_subtotal) net_revenue, 
            rcs.NAME province,
            rp.city district
            from  
            sale_order_line sol
            left join sale_order so on so.id = sol.order_id
            left join res_partner rp on rp.id = so.partner_id
            left join res_country_state rcs on rcs.id = rp.state_id 
            where 
            so.state ='sale'
            and
            so.date_order >= '%s 00:00:00' and so.date_order <= '%s 23:59:59'
            and rp.id in %s
            group by rp.id,rp.barcode, rp.NAME,rcs.NAME
            order by rp.NAME
        """ % ( self._table, start_date,end_date,customer_items )

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Tổng hợp bán hàng theo khách hàng'
        else:
            name = 'Report Sale by customers'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.general.customers' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
 
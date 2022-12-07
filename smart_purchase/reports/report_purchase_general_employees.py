from odoo import models, fields, api, tools
import datetime

class ReportPurchaseGeneralEmployee(models.Model):
    _name ='report.purchase.general.employees'
    _auto = False
    _order = "employee_name asc"

    id = fields.Integer(string='ID')
    employee_code = fields.Char(string='Employee code')
    employee_name = fields.Char(string='Employee name')
    gross_value = fields.Float(string='Gross value')
    discount = fields.Float(string='Discount')
    return_quantity = fields.Float(string='Return quantity')
    return_value = fields.Float(string='Value of return') 
    net_value = fields.Float('Net value')  
    
    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        employees = kw[0].get('employees',None)
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        employee_items = tuple(employees.ids)
        if len(employee_items)<=1:
            employee_items = employee_items + tuple('0')+tuple('0')

        sql = """
             CREATE OR REPLACE VIEW %s AS
            select 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
            rp.barcode employee_code,
            rp.NAME employee_name,
            sum(sol.product_uom_qty*sol.price_unit) gross_value ,
            sum(sol.product_uom_qty*sol.price_unit*sol.discount/100) discount,
            0 return_quantity,
            0 return_value,
            sum(sol.price_subtotal) net_value
            from  
            purchase_order_line sol
            left join purchase_order so on so.id = sol.order_id 
            left join res_users ru on ru.id = so.user_id
            left join res_partner rp on rp.id = ru.partner_id 
            where 
            so.state ='purchase'
            and
            so.date_order >= '%s 00:00:00' and so.date_order <= '%s 23:59:59'
            and rp.id  in %s 
            group by rp.id,rp.barcode, rp.NAME  
            order by rp.Name
        """ % ( self._table, start_date,end_date,employee_items )

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Tổng hợp mua hàng theo nhân viên'
        else:
            name = 'Report Purchase by employees'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.purchase.general.employees' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
 
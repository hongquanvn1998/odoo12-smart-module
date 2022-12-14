from odoo import models, fields, api, tools
import datetime

class ReportSaleGeneralEmployee(models.Model):
    _name ='report.sale.general.employees'
    _auto = False
    _order = "employee_name asc"

    id = fields.Integer(string='ID')
    employee_code = fields.Char(string='Customer code')
    employee_name = fields.Char(string='Product name')
    gross_revenue = fields.Float(string='Gross revenue')
    discount = fields.Float(string='Discount')
    return_quantity = fields.Float(string='Return quantity')
    return_value = fields.Float(string='Value of return') 
    net_revenue = fields.Float('Net revenue') 
    department = fields.Char(string='Department')
    
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
            sum(sol.product_uom_qty*sol.price_unit) gross_revenue ,
            sum(sol.product_uom_qty*sol.price_unit*sol.discount/100) discount,
            0 return_quantity,
            0 return_value,
            sum(sol.price_subtotal) net_revenue,
            ct.NAME department
            from  
            sale_order_line sol
            left join sale_order so on so.id = sol.order_id 
            left join res_users ru on ru.id = so.user_id
            left join res_partner rp on rp.id = ru.partner_id
            left join crm_team ct on ct.id = so.team_id 
            where 
            so.state ='sale'
            and
            so.date_order >= '%s 00:00:00' and so.date_order <= '%s 23:59:59'
            and rp.id  in %s 
            group by rp.id,rp.barcode, rp.NAME ,ct.NAME
            order by rp.Name
        """ % ( self._table, start_date,end_date,employee_items )

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'T???ng h???p b??n h??ng theo nh??n vi??n'
        else:
            name = 'Report Sale by employees'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.general.employees' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
 
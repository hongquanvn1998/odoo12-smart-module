from odoo import models,fields,api, tools
import datetime

class ReportPurchaseGeneralGoods(models.Model):
    _name = 'report.purchase.general.goods'
    _auto =False
    _order = 'product_name ASC'
    id = fields.Integer(string='ID')  
    product_code = fields.Char(string='Product code')
    product_name = fields.Char(string='Product name')
    unit = fields.Char(string='Unit')
    quantity = fields.Float(string='Quantity')
    gross_value = fields.Float(string='Gross value')
    discount = fields.Float(string='Discount')
    return_quantity = fields.Float(string='Return quantity')
    return_value = fields.Float(string='Value of return') 
    net_value = fields.Float('Net value')

     
    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        product_list = kw[0].get('products',None)
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        prod_items = tuple(product_list.ids)
        if len(prod_items)<=1:
            prod_items = prod_items + tuple('0')+tuple('0')

        sql = """
            CREATE OR REPLACE VIEW %s AS
            select 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
            pt.default_code product_code,
            pt.NAME product_name,
            uu.NAME unit,
            sum(pol.product_uom_qty) quantity,
            sum(pol.product_uom_qty*pol.price_unit) gross_value, 
            sum(pol.product_uom_qty*pol.price_unit*pol.discount/100) discount,
            0 return_quantity,
            0 return_value,
            sum(pol.price_subtotal) net_value 
            from 
                purchase_order_line pol 
                left join purchase_order po on po.id = pol.order_id 
                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join uom_uom uu on uu.id = pt.uom_id
                
                where po.state ='purchase'
                and 
                po.date_order >= '%s 00:00:00'  AND po.date_order <= '%s 23:59:59'
                and pt.id in %s
                group by pt.default_code, pt.NAME,uu.NAME 
                order by pt.name
        """ % ( self._table, start_date,end_date, prod_items)

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Tổng hợp mua hàng theo sản phẩm'
        else:
            name = 'Report Purchase by goods'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.purchase.general.goods' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
 

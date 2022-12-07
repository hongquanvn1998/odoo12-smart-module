from odoo import models,fields,api, tools
import datetime

class ReportPurchaseGeneralCustomers(models.Model):
    _name = 'report.purchase.general.vendors'
    _auto =False 
    _order = "vendor_name asc" 
    id = fields.Integer(string='ID')
    vendor_code = fields.Char(string='Vendor code')
    vendor_name = fields.Char(string='Vendor name')
    gross_value = fields.Float(string='Gross value')
    discount = fields.Float(string='Discount')
    return_quantity = fields.Float(string='Return quantity')
    return_value = fields.Float(string='Value of return') 
    net_value = fields.Float('Net value')
    province = fields.Char(string='Province/City')
    district = fields.Char(string='District') 
    
    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        vendors = kw[0].get('vendors',None)
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        vendor_items = tuple(vendors.ids)
        if len(vendor_items)<=1:
            vendor_items = vendor_items + tuple('0')+tuple('0')

        sql = """
             CREATE OR REPLACE VIEW %s AS
            select 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
            rp.barcode vendor_code,
            rp.NAME vendor_name,
            sum(pol.product_uom_qty*pol.price_unit) gross_value ,
            sum(pol.product_uom_qty*pol.price_unit*pol.discount/100) discount,
            0 return_quantity,
            0 return_value,
            sum(pol.price_subtotal) net_value, 
            rcs.NAME province,
            rp.city district
            from  
            purchase_order_line pol
            left join purchase_order po on po.id = pol.order_id
            left join res_partner rp on rp.id = po.partner_id
            left join res_country_state rcs on rcs.id = rp.state_id 
            where 
            po.state ='purchase'
            and
            po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59'
            and rp.id in %s
            group by rp.id,rp.barcode, rp.NAME,rcs.NAME
            order by rp.NAME
        """ % ( self._table, start_date,end_date,vendor_items )

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Tổng hợp mua hàng theo NCC'
        else:
            name = 'Report Purchase by vendors'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.purchase.general.vendors' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
 
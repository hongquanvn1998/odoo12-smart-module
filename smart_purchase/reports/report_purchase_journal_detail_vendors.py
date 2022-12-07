from odoo import models,fields,api,tools
from datetime import datetime
class ReportPurchaseJournalDetailVendor(models.Model):
    _name = 'report.purchase.journal.detail.vendors'
    _auto = False 
    _order = "document_number desc"
    id = fields.Integer(string='ID')
    posted_date = fields.Date(string='Posting date')
    document_date = fields.Datetime(string='Voucher date')
    document_number = fields.Char(string='Voucher Number')
    invoiced_date = fields.Date(string='Invoice date')
    invoice_number = fields.Char(string='Invoice number')
    description = fields.Char(string='Description')
    item_description = fields.Char(string='Item description')
    vendor_code = fields.Char(string='Vendor ID')
    vendor_name = fields.Char(string='Vendor name')
    product_code = fields.Char(string='Product code')
    product_name = fields.Char(string='Product')
    unit = fields.Char(string='Unit')
    quantity = fields.Float(string='Total quantity')
    unit_price = fields.Float(string='Unit price')
    gross_value = fields.Float(string='Gross value')
    discount = fields.Float(string='Discount')
    return_value = fields.Float(string='Value of return')    
    return_quantity = fields.Float(string='Return quantity')  


    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        vendor_list = kw[0].get('vendors',None)
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        cust_items = tuple(vendor_list.ids)
        if len(cust_items)<=1:
            cust_items = cust_items + tuple('0')+tuple('0')
        sql = """
                CREATE OR REPLACE VIEW %s AS 
                    select 
                    ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
                    po.date_approve posted_date,
                    po.date_order document_date,
                    po.NAME document_number,
                    ai.vendor_bill_number invoice_number,
                    ai.date_invoice invoiced_date,  
                    po.notes description,
                    pol.NAME item_description,
                    rp.barcode vendor_code,
                    rp.NAME vendor_name,
                    pp.default_code product_code,
                    pt.NAME product_name,
                    uu.name unit,
                    pol.product_uom_qty quantity,
                    pol.price_unit unit_price,
                    pol.product_uom_qty *  pol.price_unit  gross_value,
                    pol.product_uom_qty *  pol.price_unit*pol.discount/100 discount,
                    0 return_value,
                    0 return_quantity 
                    
                    from 
                    purchase_order_line pol 
                    left join purchase_order po on po.id = pol.order_id
                    left join res_partner rp on rp.id = po.partner_id

                    
                    left join account_invoice_line ail on ail.purchase_line_id = pol.id
                    left join account_invoice ai on ai.id = ail.invoice_id

                    left join product_product pp on pp.id = pol.product_id
                    left join product_template pt on pt.id = pp.product_tmpl_id
                    left join uom_uom uu on uu.id = pol.product_uom 
                    
                    where 
                    pol.state = 'purchase'
                    and rp.id in %s
                    and
                    po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59' 
                    order by po.NAME DESC
        """ %( self._table,cust_items,start_date,end_date)

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Sổ chi tiết mua hàng theo NCC'
        else:
            name = 'Purchase Journal Detail By Vendors'
 
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.purchase.journal.detail.vendors' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
  

from odoo import models,fields,api,tools
from datetime import datetime
class ReportSaleJournalDetail(models.Model):
    _name = 'report.sale.journal.detail.goods'
    _auto = False 
    _order = "document_number desc"
    id = fields.Integer(string='ID')
    posted_date = fields.Datetime(string='Posting date')
    document_date = fields.Datetime(string='Voucher date')
    document_number = fields.Char(string='Voucher Number')
    invoiced_date = fields.Date(string='Invoice date')
    invoice_number = fields.Char(string='Invoice number')
    description = fields.Char(string='Description')
    item_description = fields.Char(string='Item description')
    customer_code = fields.Char(string='Customer ID')
    customer_name = fields.Char(string='Customer name')
    product_code = fields.Char(string='Product code')
    product_name = fields.Char(string='Product')
    unit = fields.Char(string='Unit')
    quantity = fields.Float(string='Total quantity')
    unit_price = fields.Float(string='Unit price')
    gross_revenue = fields.Float(string='Gross revenue')
    discount = fields.Float(string='Discount')
    return_value = fields.Float(string='Value of return')    
    return_quantity = fields.Float(string='Return quantity')  


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
                    so.confirmation_date posted_date,
                    so.date_order document_date,
                    so.NAME document_number,
                    ai.invoice_number invoice_number,
                    ai.date_invoice invoiced_date,  
                    so.note description,
                    sol.NAME item_description,
                    rp.barcode customer_code,
                    rp.NAME customer_name,
                    pp.default_code product_code,
                    pt.NAME product_name,
                    uu.name unit,
                    sol.product_uom_qty quantity,
                    sol.price_unit unit_price,
                    sol.product_uom_qty *  sol.price_unit  gross_revenue,
                    sol.product_uom_qty *  sol.price_unit*sol.discount/100 discount,
                    0 return_value,
                    0 return_quantity 
                    
                    from 
                    sale_order_line sol 
                    left join sale_order so on so.id = sol.order_id
                    left join res_partner rp on rp.id = so.partner_id
                    left join product_product pp on pp.id = sol.product_id
                    left join product_template pt on pt.id = pp.product_tmpl_id
                    left join uom_uom uu on uu.id = sol.product_uom
                    
                    
                    left join sale_order_line_invoice_rel soli on soli.order_line_id = sol.id
                    left join account_invoice_line ail on ail.id = soli.invoice_line_id
                    left join account_invoice ai on ai.id = ail.invoice_id
                    
                    where 
                    sol.state = 'sale'
                    and 
                    pt.id in %s
                    and
                    so.date_order >= '%s 00:00:00' and so.date_order <= '%s 23:59:59' 
                    order by so.NAME DESC
        """ %( self._table,prod_items,start_date,end_date)

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Sổ chi tiết bán hàng theo hàng hóa'
        else:
            name = 'Sale Journal Detail By Goods'
 
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.journal.detail.goods' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
  

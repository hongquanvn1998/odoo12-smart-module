from odoo import models, fields, api, tools
import datetime

class ReportPurchaseJournal(models.Model):
    _name ='report.purchase.journal'
    _auto = False

    id = fields.Integer(string='ID')
    posted_date = fields.Date(string='Posting date')
    document_date = fields.Datetime(string='Voucher date')
    document_number = fields.Char(string='Voucher Number')
    invoiced_date = fields.Date(string='Invoice date')
    invoice_number = fields.Char(string='Invoice Number')
    description = fields.Char(string='Description') 
    goods_amount = fields.Float(string='Goods Amount')
    services_amount = fields.Float(string='Services Amount')
    other_amount = fields.Float(string='Other Amount')
    payables = fields.Float(string='Payables')
    tax_amount = fields.Float(string='Tax Amount')
    total_amount = fields.Float(string='Total Amount') 
    vendor = fields.Char(string='Vendors')
    invoice_number_display = fields.Char(string='Invoice No.', compute = '_invoice_display_convert', store=False)

    @api.model 
    @api.depends('invoice_number')
    def _invoice_display_convert(self):
        for record in self:
            if record.invoice_number is False:
                invoice = False
            else: 
                invoice = "{:07}".format(int(record.invoice_number))  
        
            record.invoice_number_display =  invoice

    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        sql = """
                CREATE OR REPLACE VIEW %s AS 
                select 
                ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
                po.date_approve posted_date, 
                po.date_order document_date, 
                po.name  document_number, 
                ai.vendor_bill_number invoice_number,
                ai.date_invoice invoiced_date, 
                po.notes description,
                sum(CASE WHEN pt.type ='product' THEN pol.price_unit *pol.product_uom_qty   ELSE  0   END) goods_amount,
                sum(CASE WHEN pt.type ='service' THEN pol.price_unit *pol.product_uom_qty ELSE  0   END) services_amount,
                sum(CASE WHEN pt.type ='consu' THEN pol.price_unit *pol.product_uom_qty ELSE  0   END) other_amount,                   
                po.amount_untaxed payables,
                sum(pol.price_tax) tax_amount ,  
                sum(pol.price_total) total_amount ,
                rp.NAME vendor 
                from  
                purchase_order po  

                left join res_partner rp on rp.id = po.partner_id
                left join purchase_order_line pol on pol.order_id = po.id
 
                left join account_invoice_line ail on ail.purchase_line_id = pol.id
                left join account_invoice ai on ai.id = ail.invoice_id

                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id

                where  
                po.state = 'purchase'
                and 
                po.date_approve >= '%s 00:00:00' and po.date_approve <= '%s 23:59:59'
                group by 
                po.name, 
                po.date_approve,po.date_order,
                ai.vendor_bill_number,
                ai.date_invoice,
                po.notes,
                po.amount_untaxed,rp.NAME 
                order by po.date_order DESC
        """ %( self._table, start_date,end_date)

        tools.drop_view_if_exists(self._cr, '%s' % self._table)
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Sổ nhật ký mua hàng'
        else:
            name = 'Purchase Journal'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.purchase.journal' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
      

   
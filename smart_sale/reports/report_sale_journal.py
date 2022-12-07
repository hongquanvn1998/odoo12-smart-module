from odoo import api, fields, models, tools
import datetime
class ReportSaleJournal(models.Model):
    _name ='report.sale.journal'
    _auto = False
    _order = "document_number desc"
    id = fields.Integer(string='ID')
    posted_date = fields.Datetime(string='Posting date')
    document_date = fields.Datetime(string='Voucher date')
    document_number = fields.Char(string='Voucher Number')
    invoiced_date = fields.Date(string='Invoice date')
    invoice_number = fields.Char(string='Invoice number')
    description = fields.Char(string='Description')
    gross_revenue = fields.Float(string='Gross revenue')
    sales_revenue = fields.Float(string='Finished product revenue')
    services_revenue = fields.Float(string='Revenue of service')
    other_revenue = fields.Float(string='Other revenues')
    discount = fields.Float(string='Discount')
    return_value = fields.Float(string='Value of return')
    sale_off_value = fields.Float('Value of price reduction')
    net_revenue = fields.Float('Net revenue')
    customer = fields.Char(string='Customer')

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
                so.confirmation_date posted_date, 
                so.date_order document_date, 
                so.name  document_number, 
                ai.invoice_number invoice_number,
                ai.date_invoice invoiced_date, 
                so.note description,
                sum(sol.price_unit* sol.product_uom_qty) gross_revenue ,
                sum(CASE WHEN pt.type ='product' THEN sol.price_unit *sol.product_uom_qty   ELSE  0   END) sales_revenue,
                sum(CASE WHEN pt.type ='service' THEN sol.price_unit *sol.product_uom_qty ELSE  0   END) services_revenue,
                sum(CASE WHEN pt.type ='consu' THEN sol.price_unit *sol.product_uom_qty ELSE  0   END) other_revenue, 
                sum( sol.price_unit *sol.product_uom_qty*sol.discount/100) discount, 
                0 return_value, 
                0 sale_off_value,
                so.amount_untaxed net_revenue,
                rp.NAME customer 
                from  
                sale_order so  

                left join res_partner rp on rp.id = so.partner_id
                left join sale_order_line sol on sol.order_id = so.id

                left join sale_order_line_invoice_rel soli on soli.order_line_id = sol.id
                left join account_invoice_line ail on ail.id = soli.invoice_line_id
                left join account_invoice ai on ai.id = ail.invoice_id

                left join product_product pp on pp.id = sol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id

                where  
                so.state = 'sale'
                and 
                so.confirmation_date >= '%s 00:00:00' and so.confirmation_date <= '%s 23:59:59'
                group by 
                so.name, 
                so.confirmation_date,so.date_order,
                ai.invoice_number
                ,ai.date_invoice,
                so.note,
                so.amount_untaxed,rp.NAME 
                order by so.date_order DESC
        """ %( self._table, start_date,end_date)

        tools.drop_view_if_exists(self._cr, '%s' % self._table)
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Sổ nhật ký bán hàng'
        else:
            name = 'Sale Journal'
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.journal' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
      

class ReportGetView(models.AbstractModel):
    _name="report.smart_sale.reportjournal_display"


    @api.model
    def _get_report_values(self,docids,data=None):
        self.env.cr.execute("""
       select * from report_sale_journal"""
        )
        report_items = self.env.cr.fetchall() 
     
        all_price_total = 0
        all_discount=0
        docs=[]
        all_total=[]
        
        for item in report_items:
           
            docs.append({
                'confirmation_date':item[1],
                'document_date':item[2],
                'document_name':item[3], 
                'invoice_no':item[4],
                'invoice_date':item[5],
                'description':item[6],
                'gross_revenue':item[7],
                'product_revenue':item[8],
                'service_revenue':item[9],
                'other_revenue':item[10],
                'discount':item[11],
                'return_value':item[12],
                'sale_off':item[13],
                'net_revenue':item[14],
                'customer':item[15],
            })
            if item[6] is None : all_price_total += all_price_total
            else:
                 all_price_total += int(item[7])

        all_total.append({
            'all_price_total':all_price_total,
            'all_discount':'',
        })
        
        return{
            # 'doc_ids':data['ids'],
            'doc_model':data['model'],
            'start_date': datetime.datetime.strptime(data['context'].get('start_date'),'%Y-%m-%d'),
            'end_date': datetime.datetime.strptime(data['context'].get('end_date'),'%Y-%m-%d'),
            'docs':docs,
            'all_total':all_total,
        }

        

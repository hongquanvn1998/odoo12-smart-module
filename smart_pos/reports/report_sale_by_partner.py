from odoo import models,fields,api,tools
from datetime import datetime
class ReportSaleByPartner(models.Model):
    _name = 'report.sale.by.partner'
    _auto = False
    id = fields.Integer(string='ID')
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')
    qty_total= fields.Integer(string='Quantity')
    amount_total= fields.Float(string='Amount Total')
    # amount_paid = fields.Float(string='Amount Paid')
    # partner_name = fields.Char(string='Partner')
    # seller_name =  fields.Char(string='Seller')
    # counter_name = fields.Char(string='Counter Name')
    partner_name = fields.Char(string='Partner')
    # partner_id = fields.Many2one('res.partner', string='Partner')


    def reload_data(self,*kw):
        # product_list = kw[0].get('filter_product',None)
        start_date = kw[0].get('start_date')
        end_date= kw[0].get('end_date')
        # filter_types=kw[0].get('filter_types')
        filter_partner=kw[0].get('filter_partner')
        # filter_employee=kw[0].get('filter_employee')
        # filter_method_payment=kw[0].get('filter_method_payment')
        # employee_items = tuple(filter_employee.ids)
        partner_items = tuple(filter_partner.ids)

        sql = """
            CREATE OR REPLACE VIEW  %s AS           
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            po.code,
            po.amount_total,
            po.qty_total,    
            po.date_order date,
            po.partner_id,
            rp.name partner_name

            FROM pos_order po left join res_partner rp on po.partner_id = rp.id
                 
            WHERE 
            po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59' 
             """ %(self._table,start_date, end_date)
   
        if len(partner_items) >0:
            sql+= """
             AND po.partner_id = %s 

            """ %  partner_items[0]

        sql+= """ 
        ORDER BY po.date_order ASC
         """ 
        if 'vi_VN' in self._context.values():
                name = 'Báo cáo theo khách hàng'
        else:
            name = 'Report partner'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.by.partner' ,
            "context":{'start_date':start_date, 'end_date':end_date}
                }
  
    #"context":{'start_date':start_date, 'search_default_code': 1 }
    # _name = 'report.end.of.day.by.sale'
    # _auto = False
    # id = fields.Integer(string='ID')
    # code_exchange = fields.Char(string='Code')
    # date = fields.Datetime(string='Date')
    # quantity = fields.Integer(string='Quantity')
    # revenue = fields.Float(string='Revenue')
    # other_revenues = fields.Float(string='Other revenues')
    # return_expenses = fields.Float(string='Return expenses')
    # payment = fields.Float(string='Real income')

    # def reload_data(self,*kw):
    #     start_date =''
    #     end_date = ''
    #     product_list = kw[0].get('filter_product',None)
    #     start_date = kw[0].get('start_date')
    #     filter_types=kw[0].get('filter_types')
    #     filter_partner=kw[0].get('filter_partner')
    #     filter_employee=kw[0].get('filter_employee')
    #     filter_method_payment=kw[0].get('filter_method_payment')
    #     employee_items = tuple(filter_employee.ids)
    #     partner_items = tuple(filter_partner.ids)
        
    #     sql = """
    #         CREATE OR REPLACE VIEW  %s AS
    #         select 
    #        *
    #         from
    #     """ %( self._table,)

    #     tools.drop_view_if_exists(self._cr, '%s' % self._table) 
    #     self.env.cr.execute(sql)
    #     return { 
    #         'name': self._table,
    #         "type": "ir.actions.act_window",
    #         "view_mode": "tree",
    #         "res_model": 'report.end.of.day.by.sale' ,
    #         "context":{'start_date':start_date,'end_date':end_date}
    #             }
  

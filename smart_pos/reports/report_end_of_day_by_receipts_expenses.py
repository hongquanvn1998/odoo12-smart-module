from odoo import models,fields,api,tools
from datetime import datetime
class ReportEndOfDayByReceiptsExpenses(models.Model):
    _name = 'report.end.of.day.by.receipts.expenses'
    _auto = False
    id = fields.Integer(string='ID')
    order_id = fields.Integer(string='Order ID') 
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')
    # quantity= fields.Integer(string='Quantity')
    # amount_total= fields.Float(string='Amount Total')
    # amount_paid = fields.Float(string='Amount Paid')
    # product_name = fields.Char(string='Product Name')
    # product_code = fields.Char(string='Product Code')
    # counter_name = fields.Char(string='Counter Name')
    receipts_expenses = fields.Float(string='Receipts Expenses')
    partner_id = fields.Many2one('res.partner', string='Partner')
   
    # partner_id = fields.One2many('res.partner', 'Partner')

    # id = fields.Integer(string='ID')
    # code_receipts_expenses = fields.Char(string='Code receipts expenses')
    # user_submitter_receiver = fields.Char(string='User submitter receiver')
    # receipts_expenses = fields.Float(string='Receipts expenses')
    # date = fields.Datetime(string='date')
    # document_number = fields.Char(string='Voucher Number')

    def reload_data(self,*kw):        
        start_date = kw[0].get('start_date')
        filter_types=kw[0].get('filter_types')

        # filter_partner=kw[0].get('filter_partner')
        # filter_employee=kw[0].get('filter_employee')
        # filter_method_payment=kw[0].get('filter_method_payment')
        # employee_items = tuple(filter_employee.ids)
        # partner_items = tuple(filter_partner.ids)   

        
        sql = """
            CREATE OR REPLACE VIEW  %s AS
            SELECT ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, tblthu.id order_id, tblthu.code code, tblthu.date_order date, tblthu.amount_paid, tblthu.amount_return, tblthu.thuchi receipts_expenses, tblthu.partner_id
  
            FROM 
            (
            select *,  amount_paid thuchi
                
            
            
            from  (select * from pos_order po where po.amount_paid > 0) receipt

            union  all   
            (select *, 
            
            CASE
                WHEN amount_return >0 THEN  amount_return * -1 
            END thuchi
            
            from pos_order po where po.amount_return >0)  

            order by  id
            ) tblthu 

             WHERE tblthu.date_order >= '%s 00:00:00' and tblthu.date_order <= '%s 23:59:59'
        """ %( self._table,start_date,start_date)

        if 'vi_VN' in self._context.values():
                name = 'Báo cáo thu chi cuối ngày'
        else:
            name = 'Report end of day by receipts expenses'

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.end.of.day.by.receipts.expenses' ,
            "context":{'start_date':start_date}
                }
    
    def reload_data_mobile(self,**kw):
        start_date = kw.get('start_date')
        is_admin = kw.get('is_admin')

        total_receipt = 0
        total_expense = 0
        total_bill = 0
        total_product = 0 
        total_revenue= 0

        create_uid = "and tblthu.create_uid = %s"%self.env.uid if is_admin == False else ""

        sql = """
            SELECT ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, tblthu.id order_id, tblthu.code code, tblthu.date_order date, tblthu.amount_paid, tblthu.amount_return, tblthu.thuchi receipts_expenses, tblthu.partner_id
  
            FROM 
            (
            select *,  amount_paid thuchi
            from  (select * from pos_order po where po.amount_paid > 0) receipt

            union  all   
            (select *, 
            
            CASE
                WHEN amount_return >0 THEN  amount_return * -1 
            END thuchi
            
            from pos_order po where po.amount_return >0)  

            order by  id
            ) tblthu 

             WHERE tblthu.date_order >= '%s 00:00:00' and tblthu.date_order <= '%s 23:59:59' %s
        """ %(start_date,start_date,create_uid)
        self.env.cr.execute(sql)
        data = self.env.cr.fetchall()

        # Lấy tổng số lượng hóa đơn
        sql_bill = """ 
        SELECT COUNT(id)
        FROM pos_order po
        WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59'
        """%(start_date,start_date)
        self.env.cr.execute(sql_bill)
        total_bill += self.env.cr.fetchall()[0][0] or 0

        # Lấy tổng số lượng sản phẩm
        sql_product = """
            SELECT SUM(pol.quantity)
            FROM pos_order_line pol 
            left join pos_order po on po.id = pol.order_id
            left join pos_counter pc on pc.id= po.counter_id

            WHERE po.date_order >= '%s 00:00:00' and po.date_order <= '%s 23:59:59'
             """ %(start_date, start_date)
        self.env.cr.execute(sql_product)
        total_product += self.env.cr.fetchall()[0][0] or 0

        for i in data:
            if i[6] >0:
                total_receipt += i[6] or 0
            else:
                total_expense += i[6] or 0
            total_revenue += i[6] or 0
        data_output = {
            "total_receipt" : total_receipt,
        "total_expense": total_expense,
        "total_bill" : total_bill,
        "total_product" : total_product ,
        "total_revenue":total_revenue,
        }
        return data_output

    def reload_data_receipt_expense_mobile(self,**kw):        
        start_date = kw.get('start_date')
        is_admin = kw.get('is_admin')

        data_output = []

        create_uid = "and tblthu.create_uid = %s"%self.env.uid if is_admin == False else ""

        sql = """
            SELECT ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, tblthu.id order_id, tblthu.code code, tblthu.date_order date, tblthu.amount_paid, tblthu.amount_return, tblthu.thuchi receipts_expenses, tblthu.partner_id
  
            FROM 
            (
            select *,  amount_paid thuchi
                
            
            
            from  (select * from pos_order po where po.amount_paid > 0) receipt

            union  all   
            (select *, 
            
            CASE
                WHEN amount_return >0 THEN  amount_return * -1 
            END thuchi
            
            from pos_order po where po.amount_return >0)  

            order by  id
            ) tblthu 

             WHERE tblthu.date_order >= '%s 00:00:00' and tblthu.date_order <= '%s 23:59:59' %s
        """ %(start_date,start_date,create_uid)

        self.env.cr.execute(sql)
        data = self.env.cr.fetchall()
        for i in data:
            dict_data={
                'id':i[1] or False,
                'bill':i[2] or False,
                'customer_name' : self.env['res.partner'].search([('id','=',i[7])]).name or False,
                'date_time':i[3] or False,
                'total_bill': i[6] or False
            }
            data_output.append(dict_data)
            
        return data_output

    def detail(self):       
        _id = self.order_id or None
        if _id is None:
            raise ValidationError('Object not exits!')
        return { 
                'name': 'Chi tiết đơn hàng ' +  self.code,
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": 'pos.order',                
                # 'res_code':_code
                 'res_id':_id,
                 'nodestroy': True,
                 'target': 'new',                 
                 'flags': {'mode': 'readonly'}
                } 

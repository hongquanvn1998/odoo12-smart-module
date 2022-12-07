from odoo import models,fields,api,tools
from datetime import datetime
# from django.core.exceptions import ValidationError
# from django.forms.utils import ValidationError

class ReportWardPointHistoryFinal(models.Model):
    _name = 'report.reward.point.history'
    _auto = False
    id = fields.Integer(string='ID')  
    order_id = fields.Integer(string='Order ID')  
    code = fields.Char(string='Code')
    date = fields.Datetime(string='Date')    
    partner_name = fields.Char(string='Partner')  
    change_point = fields.Integer(string='Change Point') 
    counter_name = fields.Char(string='Counter')
    order_name = fields.Char(string='Order Name')

    def reload_data(self,*kw):
        start_date = kw[0].get('start_date')
        end_date = kw[0].get('end_date') 

        filter_partner=kw[0].get('filter_partner')  
        partner_items = tuple(filter_partner.ids)

        sql = """
           CREATE OR REPLACE VIEW  %s AS           
           SELECT 
                ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,             
                prp.write_date date,
                po.code,
                po.name order_name,
                rp.name partner_name,
                pc.name counter_name,
                prp.change_point,
                po.id as order_id
                
            FROM pos_reward_point_history prp 
                LEFT JOIN  res_partner rp on  prp.partner_id = rp.id
                LEFT JOIN  pos_order po on prp.order_id = po.id
                LEFT JOIN  pos_counter pc on prp.counter_id = pc.id
                 
            WHERE 

            prp.write_date >= '%s 00:00:00' and prp.write_date <= '%s 23:59:59' 
             """ %(self._table,start_date, end_date)
   
        if len(partner_items) >0:
            sql+= """
             AND prp.partner_id = %s 

            """ %  partner_items[0]
        sql+= """ 
        ORDER BY prp.write_date ASC
         """ 
        if 'vi_VN' in self._context.values():
                name = 'Báo cáo lịch sử tích điểm'
        else:
            name = 'Report Reward Point History'
        
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.reward.point.history' ,
            "context":{'start_date':start_date, 'end_date':end_date}
                }
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
#'flags': {'form': {'action_buttons': False},} 
    def action_revoke(self):

        active_id = self._context.get('current_id')

        print (active_id)

        # rec = self.env['pos.orderline'].browse(int(active_id))
        _pos_order_line = self.env['pos.order.line'].search([('order_id','=',active_id)])
        view = self.env.ref('pos.form_view_xml_id')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': self.id,
            'context': self.env.context,
        }

    # def get_filtered_record(self):
    #     active_id = self._context.get('current_id')
    #     print (active_id)    

        # return { 
        #     'name': 'Chuyển trang của Thiện',        
        #     'view_mode': 'form',
        #     'view_id': False,
        #     'view_type': 'form',
        #     'res_model': 'product.pricelist',        
        #     'type': 'ir.actions.act_window',
        #     'nodestroy': True,
        #     'target': 'new',
        #     'domain': '[]'
          

        #         }
from odoo import models,fields,api,tools
from datetime import datetime

class ReportWardPointFinal(models.Model):
    _name = 'report.reward.point'
    _auto = False
    id = fields.Integer(string='ID')  
    date = fields.Datetime(string='Date')    
    partner_name = fields.Char(string='Partner')
    points = fields.Integer(string='Points') 
    reward_count = fields.Integer(string='Reward Count') 
    payment_count = fields.Integer(string='Payment Count') 


    def reload_data(self,*kw):
        start_date = kw[0].get('start_date')
        end_date = kw[0].get('end_date') 

        filter_partner=kw[0].get('filter_partner')  
        partner_items = tuple(filter_partner.ids)

        sql = """
            CREATE OR REPLACE VIEW  %s AS           
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,  rwp.write_date date ,         
            rwp.reward_count, rwp.points, rwp.payment_count , rp.name partner_name
            FROM pos_reward_point rwp 
            LEFT JOIN res_partner rp on rwp.partner_id = rp.id 
                 
            WHERE 
            rwp.write_date >= '%s 00:00:00' and rwp.write_date <= '%s 23:59:59' 
             """ %(self._table,start_date, end_date)
   
        if len(partner_items) >0:
            sql+= """
             AND rwp.partner_id = %s 

            """ %  partner_items[0]
        sql+= """ 
        ORDER BY rwp.write_date ASC
         """ 
        if 'vi_VN' in self._context.values():
                name = 'Báo cáo theo điểm'
        else:
            name = 'Report Reward Point'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.reward.point' ,
            "context":{'start_date':start_date, 'end_date':end_date}
                }
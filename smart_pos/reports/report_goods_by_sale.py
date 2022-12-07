from odoo import models,fields,api,tools
from datetime import datetime
class ReportGoodsBySale(models.Model):
    _name = 'report.goods.by.sale'
    _auto = False
    id = fields.Integer(string='ID')
    goods_code = fields.Char(string='Goods code')
    goods_name = fields.Char(string='Goods name')
    sale_quantity = fields.Integer(string='Quantity')
    revenue = fields.Float(string='Revenue')
    return_quantity=fields.Float(string='Return quantity')
    return_price=fields.Float(string='Return price')
    real_income = fields.Float(string='Real income')


    def reload_data(self,*kw):
        start_date = kw[0].get('start_date')
        end_date = kw[0].get('end_date')
        filter_goods=kw[0].get('filter_goods')
        filter_goods_category=kw[0].get('filter_goods_category')
        user_items = tuple(filter_goods.ids)
        partner_items = tuple(partner_items.ids)
        
        sql = """
            CREATE OR REPLACE VIEW  %s AS
            select 
           *
            from
        """ %( self._table,)

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': self._table,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.goods.by.sale' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }
  

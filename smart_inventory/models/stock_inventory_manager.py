from odoo import models,fields,api,tools
from datetime import datetime

class StockInventoryManager(models.Model):
    _name = 'stock.inventory.manager'
    _auto = False 
    product_code = fields.Char(string='Product code')
    product_name = fields.Char(string ='Product name')
    unit = fields.Char(string='Unit')
    warehouse = fields.Integer(string='Warehouse')
    warehouse_code = fields.Char(string='Warehouse code')
    warehouse_name = fields.Char(string='Warehouse name') 
    opening_quantity = fields.Integer(string='Opening quantity')
    opening_value = fields.Float(string='Opening value')
    import_quantity = fields.Integer(string='Inward quantity')
    import_value = fields.Float(string='Inward value')
    export_quantity = fields.Integer(string='Outward quantity')
    export_value = fields.Float(string='Outward value')
    closing_quantity = fields.Integer(string='Closing quantity')
    closing_value = fields.Float(string='Closing value')
    pid = fields.Integer(string='Product ID')  
    @api.model_cr
    def init(self): 
        sql =  """
            CREATE OR REPLACE VIEW %s AS
            select 
                ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
                CASE WHEN stock_open.pcode IS NOT NULL THEN stock_open.pcode ELSE stock_change.pcode END product_code,
                CASE WHEN stock_open.pname IS NOT NULL THEN stock_open.pname ELSE stock_change.pname END product_name,
                CASE WHEN stock_open.punit IS NOT NULL THEN stock_open.punit ELSE stock_change.punit END unit,
                CASE WHEN stock_open.wloc IS NOT NULL THEN stock_open.wloc ELSE stock_change.wloc END warehouse,
                CASE WHEN stock_open.wcode IS NOT NULL THEN stock_open.wcode ELSE stock_change.wcode END warehouse_code,
                CASE WHEN stock_open.wname IS NOT NULL THEN stock_open.wname ELSE stock_change.wname END warehouse_name,
                COALESCE( COALESCE(stock_open.in_quantity,0) - COALESCE(stock_open.out_quantity,0),0)   opening_quantity,
                COALESCE(COALESCE(stock_open.in_value) - COALESCE(abs(stock_open.out_value),0),0) opening_value,
                COALESCE(stock_change.in_quantity,0) import_quantity ,
                COALESCE(stock_change.in_value,0) import_value,
                COALESCE(stock_change.out_quantity,0 ) export_quantity,
                COALESCE(stock_change.out_value,0) export_value, 
                COALESCE(stock_open.in_quantity,0) - COALESCE(stock_open.out_quantity,0) + COALESCE(stock_change.in_quantity,0) - COALESCE(abs(stock_change.out_quantity),0) closing_quantity,
                COALESCE(stock_open.in_value,0) - COALESCE(abs(stock_open.out_value),0) + COALESCE(stock_change.in_value,0) - COALESCE(abs(stock_change.out_value),0) closing_value
                ,CASE WHEN stock_open.pid IS NOT NULL THEN stock_open.pid ELSE stock_change.pid END pid                    
                from
                (select
                opening.id pid,
                opening.pcode,
                opening.pname,
                opening.punit,
                opening.wloc,
                opening.wcode,
                opening.wname,
                sum(opening.in_quantity) in_quantity,
                sum(opening.in_value) in_value,
                sum(opening.out_quantity) out_quantity,
                sum(opening.out_value) out_value,
                sum(opening.sum)
                from
                (select 
                pp.id, 
                pp.default_code pcode,
                pt.NAME pname,  
                uu.name punit,
                (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) wloc, 
                (select sw.code from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wcode,
                (select sw.name from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wname,

                COALESCE(sum(case when sm.value >0 then sml.qty_done end),0) in_quantity,
                COALESCE(sum(case when sm.value >0 then sm.value end),0) in_value,
                
                COALESCE(sum(case when sm.VALUE < 0 then sml.qty_done end),0) out_quantity ,   
                COALESCE(sum(case when sm.VALUE < 0 then sm.value end),0) out_value,
                sum(sm.VALUE) 
                from 
                stock_move_line sml  
                left join product_product pp on sml.product_id = pp.id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join stock_move sm on sm.id = sml.move_id
                left join uom_uom uu on uu.id = sml.product_uom_id 
                where sml.state ='done' and
                sml.DATE < '%s'
                GROUP BY wcode,wname, pp.id, pp.default_code,pt.NAME, uu.NAME ,sm.location_dest_id, sm.location_id,wloc, sm.VALUE
                order by wloc) opening 
                group by
                pid,
                opening.pcode,
                opening.pname,
                opening.punit,
                opening.wloc,
                opening.wcode,
                opening.wname 
                order by wloc) stock_open

                full join

                (select
                incurred.id pid,
                incurred.pcode,
                incurred.pname,
                incurred.punit,
                incurred.wloc,
                incurred.wcode,
                incurred.wname,
                sum(incurred.in_quantity) in_quantity,
                sum(incurred.in_value) in_value,
                sum(incurred.out_quantity) out_quantity,
                sum(incurred.out_value) out_value,
                sum(incurred.sum)
                from
                (select pp.id, 
                pp.default_code pcode,
                pt.NAME pname,  
                uu.name punit,
                (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) wloc, 
                (select sw.code from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wcode,
                (select sw.name from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wname,

                COALESCE(sum(case when sm.value >0 then sml.qty_done end),0) in_quantity,
                COALESCE(sum(case when sm.value >0 then sm.value end),0) in_value,
                
                COALESCE(sum(case when sm.VALUE < 0 then sml.qty_done end),0) out_quantity ,   
                COALESCE(sum(case when sm.VALUE < 0 then sm.value end),0) out_value,
                sum(sm.VALUE) 
                from 
                stock_move_line sml  
                left join product_product pp on sml.product_id = pp.id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join stock_move sm on sm.id = sml.move_id
                left join uom_uom uu on uu.id = sml.product_uom_id 
                where sml.state ='done' 
                and
                sml.DATE >= '%s' and sml.DATE <= '%s 23:59:59' 

                GROUP BY wcode,wname, pp.id, pp.default_code,pt.NAME, uu.NAME ,sm.location_dest_id, sm.location_id,wloc, sm.VALUE
                order by wloc) incurred

                group by
                pid,
                incurred.pcode,
                incurred.pname,
                incurred.punit,
                incurred.wloc,
                incurred.wcode,
                incurred.wname 
                order by wloc) stock_change
                on stock_change.pid = stock_open.pid and stock_change.wloc = stock_open.wloc
                            """ % (self._table, '2019-12-01' ,'2019-12-01','2019-12-31')
        tools.drop_view_if_exists(self._cr, '%s' % self._table)
        self.env.cr.execute(sql)
 
    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        sql =  """
            CREATE OR REPLACE VIEW %s AS
            select 
                ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
                CASE WHEN stock_open.pcode IS NOT NULL THEN stock_open.pcode ELSE stock_change.pcode END product_code,
                CASE WHEN stock_open.pname IS NOT NULL THEN stock_open.pname ELSE stock_change.pname END product_name,
                CASE WHEN stock_open.punit IS NOT NULL THEN stock_open.punit ELSE stock_change.punit END unit,
                CASE WHEN stock_open.wloc IS NOT NULL THEN stock_open.wloc ELSE stock_change.wloc END warehouse,
                CASE WHEN stock_open.wcode IS NOT NULL THEN stock_open.wcode ELSE stock_change.wcode END warehouse_code,
                CASE WHEN stock_open.wname IS NOT NULL THEN stock_open.wname ELSE stock_change.wname END warehouse_name,
                COALESCE( COALESCE(stock_open.in_quantity,0) - COALESCE(stock_open.out_quantity,0),0)   opening_quantity,
                COALESCE(COALESCE(stock_open.in_value) - COALESCE(abs(stock_open.out_value),0),0) opening_value,
                COALESCE(stock_change.in_quantity,0) import_quantity ,
                COALESCE(stock_change.in_value,0) import_value,
                COALESCE(stock_change.out_quantity,0 ) export_quantity,
                COALESCE(stock_change.out_value,0) export_value, 
                COALESCE(stock_open.in_quantity,0) - COALESCE(stock_open.out_quantity,0) + COALESCE(stock_change.in_quantity,0) - COALESCE(abs(stock_change.out_quantity),0) closing_quantity,
                COALESCE(stock_open.in_value,0) - COALESCE(abs(stock_open.out_value),0) + COALESCE(stock_change.in_value,0) - COALESCE(abs(stock_change.out_value),0) closing_value
                ,CASE WHEN stock_open.pid IS NOT NULL THEN stock_open.pid ELSE stock_change.pid END pid                    
                from
                (select
                opening.id pid,
                opening.pcode,
                opening.pname,
                opening.punit,
                opening.wloc,
                opening.wcode,
                opening.wname,
                sum(opening.in_quantity) in_quantity,
                sum(opening.in_value) in_value,
                sum(opening.out_quantity) out_quantity,
                sum(opening.out_value) out_value,
                sum(opening.sum)
                from
                (select 
                pp.id, 
                pp.default_code pcode,
                pt.NAME pname,  
                uu.name punit,
                (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) wloc, 
                (select sw.code from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wcode,
                (select sw.name from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wname,

                COALESCE(sum(case when sm.value >0 then sml.qty_done end),0) in_quantity,
                COALESCE(sum(case when sm.value >0 then sm.value end),0) in_value,
                
                COALESCE(sum(case when sm.VALUE < 0 then sml.qty_done end),0) out_quantity ,   
                COALESCE(sum(case when sm.VALUE < 0 then sm.value end),0) out_value,
                sum(sm.VALUE) 
                from 
                stock_move_line sml  
                left join product_product pp on sml.product_id = pp.id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join stock_move sm on sm.id = sml.move_id
                left join uom_uom uu on uu.id = sml.product_uom_id 
                where sml.state ='done' and
                sml.DATE < '%s'
                GROUP BY wcode,wname, pp.id, pp.default_code,pt.NAME, uu.NAME ,sm.location_dest_id, sm.location_id,wloc, sm.VALUE
                order by wloc) opening 
                group by
                pid,
                opening.pcode,
                opening.pname,
                opening.punit,
                opening.wloc,
                opening.wcode,
                opening.wname 
                order by wloc) stock_open

                full join

                (select
                incurred.id pid,
                incurred.pcode,
                incurred.pname,
                incurred.punit,
                incurred.wloc,
                incurred.wcode,
                incurred.wname,
                sum(incurred.in_quantity) in_quantity,
                sum(incurred.in_value) in_value,
                sum(incurred.out_quantity) out_quantity,
                sum(incurred.out_value) out_value,
                sum(incurred.sum)
                from
                (select pp.id, 
                pp.default_code pcode,
                pt.NAME pname,  
                uu.name punit,
                (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) wloc, 
                (select sw.code from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wcode,
                (select sw.name from stock_warehouse sw where sw.lot_stock_id = (case when sm.Value > 0 then sm.location_dest_id else sm.location_id end) ) wname,

                COALESCE(sum(case when sm.value >0 then sml.qty_done end),0) in_quantity,
                COALESCE(sum(case when sm.value >0 then sm.value end),0) in_value,
                
                COALESCE(sum(case when sm.VALUE < 0 then sml.qty_done end),0) out_quantity ,   
                COALESCE(sum(case when sm.VALUE < 0 then sm.value end),0) out_value,
                sum(sm.VALUE) 
                from 
                stock_move_line sml  
                left join product_product pp on sml.product_id = pp.id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join stock_move sm on sm.id = sml.move_id
                left join uom_uom uu on uu.id = sml.product_uom_id 
                where sml.state ='done' 
                and
                sml.DATE >= '%s' and sml.DATE <= '%s 23:59:59' 

                GROUP BY wcode,wname, pp.id, pp.default_code,pt.NAME, uu.NAME ,sm.location_dest_id, sm.location_id,wloc, sm.VALUE
                order by wloc) incurred

                group by
                pid,
                incurred.pcode,
                incurred.pname,
                incurred.punit,
                incurred.wloc,
                incurred.wcode,
                incurred.wname 
                order by wloc) stock_change
                on stock_change.pid = stock_open.pid and stock_change.wloc = stock_open.wloc
                            """ % (self._table, start_date ,start_date, end_date)
        tools.drop_view_if_exists(self._cr, '%s' % self._table)
        self.env.cr.execute(sql)
        return { 
            'name': 'Tồn kho',
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'stock.inventory.manager' ,
            "context":{'search_default_groupby_warehouse_name': 1,'start_date':start_date,'end_date':end_date}
                }
    
    
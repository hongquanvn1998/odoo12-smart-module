from odoo import models,fields,api

class StockInventoryReport(models.AbstractModel):
    _name="stock.inventory.report"
    # _auto = False

    # start_date = fields.Date('Start date',compute="default_get")
    # end_date = fields.Date('End date',compute="default_get")
    # warehouse = fields.Char(string="Warehouse",compute="default_get")
    # product_code = fields.Char("Product code",compute="default_get")
    # product_name = fields.Char("Product name",compute="default_get")
    # unit_of_product = fields.Char("Product units",compute="default_get")
    # openning_quantity = fields.Float("Openning quantity",compute="default_get")
    # openning_value      = fields.Float("Openning value",compute="default_get")

    # import_quantity = fields.Float("Import quantity",compute="default_get")
    # import_value      = fields.Float("Import value",compute="default_get")

    # export_quantity = fields.Float("Export quantity",compute="default_get")
    # export_value      = fields.Float("Export value",compute="default_get") 

    # closing_quantity = fields.Float("Closing quantity",compute="default_get")
    # closing_value      = fields.Float("Closing value",compute="default_get")   

    # @api.model
    # def init(self): 
    #     print("Ghi nhan moi")
        # self.product_code = '1'
        # self.product_name = "Thong so moi san pham 1"
        # self.openning_quantity = 34
    # @api.model
    @api.model
    def _get_report_values(self, docids, data=None):
        self.ensure_one()
        print ("Da goi khi load")
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        warehouse= data['form']['warehouse']
        
        res = self.env.cr.execute( """select sml.product_id, pt.NAME,sml.location_dest_id,sm.warehouse_id, spt.code code , 
        CASE  WHEN  spt.code='outgoing' THEN  sum(sm.VALUE)  end giatrixuat,
        CASE WHEN spt.code ='outgoing' THEN sum(sml.qty_done) end soluongxuat,

        CASE  WHEN  spt.code='incoming' THEN  sum(sm.VALUE)  end giatrinhap,
        CASE WHEN spt.code ='incoming' THEN sum(sml.qty_done) end soluongnhap

        --  count(*) total_record
        --, sum(sml.qty_done), sum(sm.value) total 
        from stock_move_line sml
        inner join stock_move sm on sm.id = sml.move_id
        left join product_product pp on pp.id = sml.product_id
        left join product_template pt on pt.id = pp.product_tmpl_id
        left join stock_warehouse sw on sw.id = sm.warehouse_id
        inner join stock_picking sp on sp.id = sm.picking_id
        inner join stock_picking_type spt on spt.id = sp.picking_type_id

        where

        sml.state='done'

        and sml.date >= '2019-09-09'
        and sml.date <= '2019-09-10'

        group by sml.product_id,pt.Name,sml.location_dest_id,sm.warehouse_id, spt.code""")
        result = self.env.cr.fetchall()
        
        for record in result:
            self.openning_quantity = record[6]
            self.openning_value = record[5]
        #return result

             


 

    def _check_something(self,params):
        print("da goi vo day roi ")


    # @api.model
    # @api.onchange("start_date","end_date","warehouse")
    # def _stock_inventory_calculate(self):
    #     for record in self:
    #         stock_move_ids = self.env['stock.move.line'].search([()])
    #         for stock_move_id in stock_move_ids:
    #             record.product_code = stock_move_id.product_id.barcode
    #             record.product_name =  stock_move_id.product_id.name
    #             # record.openning_quantity = stock_move_id.


# select sml.product_id, pt.NAME,sml.location_dest_id,sm.warehouse_id, spt.code code , 
# CASE  WHEN  spt.code='outgoing' THEN  sum(sm.VALUE)  end giatrixuat,
# CASE WHEN spt.code ='outgoing' THEN sum(sml.qty_done) end soluongxuat,

# CASE  WHEN  spt.code='incoming' THEN  sum(sm.VALUE)  end giatrinhap,
# CASE WHEN spt.code ='incoming' THEN sum(sml.qty_done) end soluongnhap

# --  count(*) total_record
#   --, sum(sml.qty_done), sum(sm.value) total 
#   from stock_move_line sml
# inner join stock_move sm on sm.id = sml.move_id
# left join product_product pp on pp.id = sml.product_id
# left join product_template pt on pt.id = pp.product_tmpl_id
# left join stock_warehouse sw on sw.id = sm.warehouse_id
# inner join stock_picking sp on sp.id = sm.picking_id
# inner join stock_picking_type spt on spt.id = sp.picking_type_id

# where

# sml.state='done'

# and sml.date >= '2019-09-09'
# and sml.date <= '2019-09-10'

# group by sml.product_id,pt.Name,sml.location_dest_id,sm.warehouse_id, spt.code

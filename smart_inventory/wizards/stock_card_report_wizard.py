from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class StockCardWizard(models.TransientModel):
    _name ='stock.card.wizard'
    #_auto = False
    filter_date= fields.Selection(
        string=u'',
        selection=[
            ('0', 'From the beginning of month to the present'), 
            ('1', 'This quarter'),
            ('2', 'From the early quarter to the present'),
            ('3', 'This year'),
            ('4', 'From the beginning of the year to present'),
            ('5', 'The first half of the year'),
            ('6', 'The last half of the year '),
            ],
            default="0"
    )

    start_date = fields.Date(required=True, default=str(datetime.today().replace(day=1)))
    end_date = fields.Date(required=True, default=fields.Date.today)
    warehouse = fields.Many2one("stock.location",string="Warehouse")
    overall_count =  fields.Boolean(
        string='Overall count', default=False
    )
    

    @api.onchange('filter_date')
    def get_date(self):
        if self.filter_date is False : pass
        else:
            t= self.getmonth(self)
            if int(self.filter_date) ==0 :
                    self.start_date = str(datetime.today().replace(day=1))
            if int(self.filter_date) ==1 :
                    self.start_date = t['start_date']
                    self.end_date= t['end_date']
            if int(self.filter_date) ==2 :
                    self.start_date = t['start_date']
                    self.end_date = str(datetime.today())
            if int(self.filter_date) ==3 :
                    self.start_date = str(datetime.today().replace(day=1,month=1))
                    self.end_date = str(datetime.today().replace(day=31,month=12))
            if int(self.filter_date) ==4 :
                    self.start_date = str(datetime.today().replace(day=1,month=1))
                    self.end_date = str(datetime.today())
            if int(self.filter_date) ==5 :
                    self.start_date = str(datetime.today().replace(day=1,month=1))
                    self.end_date = str(datetime.today().replace(day=30,month=6))
            if int(self.filter_date) ==6 :
                    self.start_date = str(datetime.today().replace(day=1,month=7))
                    self.end_date = str(datetime.today().replace(day=31,month=12))
    @staticmethod
    def getmonth(self):
        currentMonth = datetime.now().month
        if 1 <currentMonth <=3 :
            self.start_date = str(datetime.today().replace(day=1,month=1))
            self.end_date = str(datetime.today().replace(day=31,month=3))
        if 3< currentMonth <=6 :
            self.start_date = str(datetime.today().replace(day=1,month=4))
            self.end_date = str(datetime.today().replace(day=30,month=6))
        if 6< currentMonth <=9:
            self.start_date = str(datetime.today().replace(day=1,month=7))
            self.end_date = str(datetime.today().replace(day=30,month=9))
        else:
            self.start_date = str(datetime.today().replace(day=1,month=10))
            self.end_date = str(datetime.today().replace(day=31,month=12))
        return  {'start_date': self.start_date, 'end_date': self.end_date} 

    def get_report(self): 
        data ={
            'ids': self.ids,
            'model': self._name,
            'form': {
                 'warehouse': self.warehouse, 
                 'combine':self.overall_count,
                 'start_date': self.start_date,
                 'end_date': self.end_date
            },
        }
        return self.env.ref('smart_inventory.stock_card_report').report_action(self, data=data) 


class GetReportView(models.AbstractModel):
    _name="report.smart_inventory.stock_card_report_template"

    @api.model
    def _get_report_values(self, docids, data=None):
        sql_command =''
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        warehouse= data['form']['warehouse']
        combine = data['form']['combine']
        if not combine: 
            sql_command = """
                            select
                                bcd.date document_date,
                                bcd.reference document_number,
                                CASE WHEN xyz.default_code is not null THEN xyz.default_code ELSE bcd.pcode END product_code ,
                                CASE WHEN xyz.product_name is not null THEN xyz.product_name ELSE bcd.pname END product_name ,
                                CASE WHEN xyz.warehouse is not null THEN xyz.warehouse ELSE bcd.warehouse END warehouse ,
                                CASE WHEN xyz.warehouse_code is not null THEN xyz.warehouse_code ELSE bcd.warehouse_code END warehouse_code ,
                                CASE WHEN xyz.warehouse_name is not null THEN xyz.warehouse_name ELSE bcd.warehouse_name END warehouse_name,
                                CASE WHEN xyz.unit is not null THEN xyz.unit ELSE bcd.unit END unit,
                                COALESCE(xyz.opening_stock,0)  opening_stock,
                                COALESCE(bcd.import_quantity,0) import_quantity,
                                COALESCE(bcd.export_quantity,0)  export_quantity,
                                bcd.note,
                                bcd.id       
                        from 

                        (select ost.default_code, ost.product_name,ost.warehouse, ost.warehouse_code,ost.warehouse_name,ost.unit,
                        (COALESCE(sum(ost.import_quantity),0) - COALESCE(sum(ost.export_quantity) ,0)) opening_stock

                        from 
                        ( 
                        select pp.default_code, pt.NAME product_name,  uom.name unit,
                         sm.value , 
                         CASE WHEN sm.value < 0 THEN  sml.location_id ELSE sml.location_dest_id  end warehouse,
                         CASE WHEN sm.value < 0 THEN  (select code from stock_warehouse sw where sw.lot_stock_id= sml.location_id)
                                                           ELSE (select code from stock_warehouse sw where sw.lot_stock_id=sml.location_dest_id)  end warehouse_code,                                                      
                         CASE WHEN sm.value < 0 THEN  (select name from stock_warehouse sw where sw.lot_stock_id= sml.location_id)
                                                            ELSE (select name from stock_warehouse sw where sw.lot_stock_id=sml.location_dest_id)  end warehouse_name,                  
                         CASE WHEN sm.value < 0 THEN sum(sml.qty_done) end export_quantity,  
                         CASE WHEN sm.value > 0  THEN sum(sml.qty_done) end import_quantity

                        from 

                        stock_move_line sml

                        join product_product pp on pp.id = sml.product_id
                        join product_template pt on pt.id = pp.product_tmpl_id
                        join stock_move sm on sm.id = sml.move_id
                        join uom_uom uom on uom.id = sml.product_uom_id

                        where sml.state ='done'
                        and
                        sml.date < '%s'

                        group by pp.default_code,sml.product_id, pt.NAME, sml.location_id,sml.location_dest_id, uom.name, sm.value 
                        order by sml.product_id ASC 
                        ) ost group by ost.default_code,ost.product_name, ost.warehouse,ost.warehouse_code,ost.warehouse_name, ost.unit)
                        xyz

                        full join ( 
                        select 
                        _sml.id,
                        _sml.date,
                        _sml.reference,
                        _pp.default_code pcode, _pt.NAME pname,
                                CASE WHEN sm.value < 0 THEN  _sml.location_id ELSE _sml.location_dest_id  end warehouse,
                                CASE WHEN sm.value < 0 THEN  (select code from stock_warehouse sw where sw.lot_stock_id= _sml.location_id)
                                   ELSE   (select code from stock_warehouse sw where sw.lot_stock_id=_sml.location_dest_id)  end warehouse_code,
                                CASE WHEN sm.value < 0 THEN  (select name from stock_warehouse sw where sw.lot_stock_id= _sml.location_id)
                                  ELSE   (select name from stock_warehouse sw where sw.lot_stock_id=_sml.location_dest_id)  end warehouse_name,
                                uom.name unit,
                                _sml.qty_done, _sm.note ,
                                CASE WHEN sm.value > 0 THEN  _sml.qty_done  end import_quantity,
                                CASE WHEN sm.value < 0 THEN  _sml.qty_done  end export_quantity
                                                        
                        from stock_move_line _sml
                        left join stock_move _sm on _sm.id = _sml.move_id 
                        join product_product _pp on _pp.id = _sml.product_id
                        join product_template _pt on _pt.id = _pp.product_tmpl_id 
                        join stock_move sm on sm.id = _sml.move_id
                        join uom_uom uom on uom.id = _sml.product_uom_id
                        
                        where 
                        _sml.state ='done' AND
                        _sml.DATE >= '%s' and _sml.DATE <= '%s 23:59:59'
                        order by _sml.product_id, _sml.date, _sml.id ASC

                        ) bcd on bcd.pcode = xyz.default_Code
                        order by warehouse,product_code, id
                                 """ % (start_date,start_date, end_date)
        else:
            sql_command = """
                                select combine.document_date, combine.document_number,combine.product_code,combine.product_name, 
                                'all' warehouse,'all' warehouse_code,'Tất cả kho' warehouse_name, combine.unit, 
                                sum(combine.opening_stock) open_stock, 
                                sum(combine.import_quantity) import_quantity, 
                                sum(combine.export_quantity) export_quantity,combine.note  
                                from
                                (select   
                                bcd.date document_date,
                                bcd.reference document_number,
                                CASE WHEN xyz.default_code is not null THEN xyz.default_code ELSE bcd.pcode END product_code ,
                                CASE WHEN xyz.product_name is not null THEN xyz.product_name ELSE bcd.pname END product_name ,
                                CASE WHEN xyz.warehouse is not null THEN xyz.warehouse ELSE bcd.warehouse END warehouse ,
                                CASE WHEN xyz.warehouse_code is not null THEN xyz.warehouse_code ELSE bcd.warehouse_code END warehouse_code ,
                                CASE WHEN xyz.warehouse_name is not null THEN xyz.warehouse_name ELSE bcd.warehouse_name END warehouse_name,
                                CASE WHEN xyz.unit is not null THEN xyz.unit ELSE bcd.unit END unit,
                                COALESCE(xyz.opening_stock,0)  opening_stock,
                                COALESCE(bcd.import_quantity,0) import_quantity,
                                COALESCE(bcd.export_quantity,0)  export_quantity,
                                bcd.note       
                        from 

                        (select ost.default_code, ost.product_name,ost.warehouse, ost.warehouse_code,ost.warehouse_name,ost.unit,
                        (COALESCE(sum(ost.import_quantity),0) - COALESCE(sum(ost.export_quantity) ,0)) opening_stock

                        from 
                        ( 
                        select pp.default_code, pt.NAME product_name,  uom.name unit,
                         sm.value , 
                         CASE WHEN sm.value < 0 THEN  sml.location_id ELSE sml.location_dest_id  end warehouse,
                         CASE WHEN sm.value < 0 THEN  (select code from stock_warehouse sw where sw.lot_stock_id= sml.location_id)
                                                           ELSE (select code from stock_warehouse sw where sw.lot_stock_id=sml.location_dest_id)  end warehouse_code,
                                                       
                         CASE WHEN sm.value < 0 THEN  (select name from stock_warehouse sw where sw.lot_stock_id= sml.location_id)
                                                            ELSE (select name from stock_warehouse sw where sw.lot_stock_id=sml.location_dest_id)  end warehouse_name,
                                                    
                         CASE WHEN sm.value < 0 THEN sum(sml.qty_done) end export_quantity,  
                         CASE WHEN sm.value > 0  THEN sum(sml.qty_done) end import_quantity

                        from 

                        stock_move_line sml

                        join product_product pp on pp.id = sml.product_id
                        join product_template pt on pt.id = pp.product_tmpl_id
                        join stock_move sm on sm.id = sml.move_id
                        join uom_uom uom on uom.id = sml.product_uom_id

                        where sml.state ='done'
                        and
                        sml.date < '%s'

                        group by pp.default_code,sml.product_id, pt.NAME, sml.location_id,sml.location_dest_id, uom.name, sm.value 
                        order by sml.product_id  ASC 
                        ) ost group by ost.default_code,ost.product_name, ost.warehouse,ost.warehouse_code,ost.warehouse_name, ost.unit)
                        xyz

                        full join ( 
                        select 
                        _sml.date,
                        _sml.reference,
                        _pp.default_code pcode, _pt.NAME pname,
                                CASE WHEN sm.value < 0 THEN  _sml.location_id ELSE _sml.location_dest_id  end warehouse,
                                CASE WHEN sm.value < 0 THEN  (select code from stock_warehouse sw where sw.lot_stock_id= _sml.location_id)
                                   ELSE   (select code from stock_warehouse sw where sw.lot_stock_id=_sml.location_dest_id)  end warehouse_code,
                                CASE WHEN sm.value < 0 THEN  (select name from stock_warehouse sw where sw.lot_stock_id= _sml.location_id)
                                  ELSE   (select name from stock_warehouse sw where sw.lot_stock_id=_sml.location_dest_id)  end warehouse_name,
                                uom.name unit,
                                _sml.qty_done, _sm.note ,
                                CASE WHEN sm.value > 0 THEN  _sml.qty_done  end import_quantity,
                                CASE WHEN sm.value < 0 THEN  _sml.qty_done  end export_quantity
                                                        
                        from stock_move_line _sml
                        left join stock_move _sm on _sm.id = _sml.move_id 
                        join product_product _pp on _pp.id = _sml.product_id
                        join product_template _pt on _pt.id = _pp.product_tmpl_id 
                        join stock_move sm on sm.id = _sml.move_id
                        join uom_uom uom on uom.id = _sml.product_uom_id
                        
                        where 
                        _sml.state ='done' AND
                        _sml.DATE >= '%s' 

                        and _sml.DATE <= '%s 23:59:59'
                        order by _sml.product_id, _sml.date, _sml.id ASC 
                        ) bcd on bcd.pcode = xyz.default_Code 
                        order by product_code) combine
                        
                        group by combine.product_code, combine.product_name,  combine.unit,
                        combine.document_number, combine.note,combine.document_date
                        order by combine.product_code, combine.document_number

            """ % (start_date,start_date, end_date)
        self.env.cr.execute(sql_command)
        records =  self.env.cr.fetchall()
        _begin = False
        products = []
        product = {}
        _pid = 0
        _length =0
        for item in records:
            _length+=1
            if item[3] != _pid:
                if _length > 1:
                    products.append(product)
                    product={}

                _item =[]
                _item.append(item) 
                product.update({
                    'product_code':item[2],
                    'product_name':item[3],
                    'warehouse_code':item[5],
                    'warehouse_name':item[6],
                    'open_stock':item[8], 
                    'product_unit':item[7],
                    'items': _item
                })
                _pid = item[3]
            else:
                _items =  product.get('items')
                _items.append(item)
                product.update({'items':_items })
             
            if _length == len(records) :
                    products.append(product) 

        # print(products)   
        return   {
            'start_date':start_date,
            'end_date':end_date,
            'docs':products
            }

 
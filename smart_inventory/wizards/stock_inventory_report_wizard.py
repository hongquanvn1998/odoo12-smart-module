from odoo import models,fields,api,_ 
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
class InventoryWizard(models.TransientModel) :
    _name ='inventory.wizard'
   # _auto = False
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
            ], default='0'
    )

    start_date = fields.Date(required=True, default=str(datetime.today().replace(day=1)))
    end_date = fields.Date(required=True, default=fields.Date.today)
    warehouse = fields.Many2one("stock.location",string="Warehouse")

 
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
                 'start_date': self.start_date,
                 'end_date': self.end_date
            },
        }
        return self.env.ref('smart_inventory.stock_inventory_report').report_action(self, data=data) 

    # @api.multi
    def set_params_to_list(self):  
        params = {
            'start_date':self.start_date,
            'end_date': self.end_date
        } 
        return self.env.get('stock.inventory.manager').reload_data(params)

class GetReportView(models.AbstractModel):
    _auto = False 
    _name ="report.smart_inventory.stock_inventory_report_template"

    @api.model
    def _get_report_values(self, docids, data=None): 
        self.env.cr.execute("""
        select product_code,product_name,unit,warehouse,warehouse_code,warehouse_name,opening_quantity,opening_value,import_quantity,
        import_value,export_quantity,export_value,closing_quantity,closing_value from stock_inventory_manager"""
        )
        _transfer_items = self.env.cr.fetchall() 
         
        stock = self._stock_calculate(_transfer_items) 
  
        return   {
            'start_date': datetime.strptime(data['context'].get('start_date'),'%Y-%m-%d'),
            'end_date': datetime.strptime(data['context'].get('end_date'),'%Y-%m-%d'),
            'docs':stock
        } 
    @staticmethod
    def _stock_calculate(stock_list):
        if len(stock_list)<=0:
            return [] 
        wid = 0
        warehouses =[]
        warehouse={}
        length = 0
        for item in stock_list:
            length+=1
            if item[3] != wid:
                if length >1 :
                    warehouses.append(warehouse)
                    warehouse = {} 
                _item =[]
                
                _item.append(item) 
                warehouse.update({
                    'warehouse_code':item[4],
                    'warehouse_name':item[5],
                    'items': _item
                })
                wid = item[3]
            else: 
                _items =  warehouse.get('items')
                _items.append(item)
                warehouse.update({'items':_items })

            if length == len(stock_list) :
                warehouses.append(warehouse)
                _group_end = False
        return warehouses

    
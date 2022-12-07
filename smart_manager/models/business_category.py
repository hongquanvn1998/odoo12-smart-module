

from odoo import models, fields, api , _
class BusinessCategory (models.Model):
    _name = 'smart_manager.business_category'
    _description ='Business Categories'

    name =   fields.Char(
        string='Business Category',
    )

    code =   fields.Char(
        string='Code',
    ) 

    icon =   fields.Binary(
        string='Icon',
    ) 
    
class PaymentPeriod(models.Model):
    _name ="smart_manager.payment_period"
    _description = 'Payment Period'

    name = fields.Char(string='Payment Period Name')
    is_annualy =   fields.Boolean(
        string='Annualy',
    )
    value =   fields.Integer(
        string='Value',
    )
    note =  fields.Text(
        string='Note',
    )

class AppPrice(models.Model):
    _name ='smart_manager.app_price'
    _description =' App Price'

    name = fields.Char()

    app =   fields.Many2one(
        string='App Module',
        comodel_name='product.template',
        ondelete='restrict',
    )
    period =  fields.Many2one(
        string='Payment Period',
        comodel_name='smart_manager.payment_period',
        ondelete='restrict',
    )
    price =     fields.Float(
        string='Price',
    ) 
    enable =  fields.Boolean(
        string='Activate',
        default=True
    )
    
   
    @api.onchange('app') 
    def app_change(self):
        self.name = _('%s trong %s') % ( self.app.name,self.period.name )
 
    def dict_parse(self):
        return [{
            'id':record['id'],
            'appId': record['app'].id,
            'appName':record['app'].name,
            'periodId':record['period'].id,
            'isAnnualy': record['period'].is_annualy,
            'periodValue':record['period'].value,
            'periodName':record['period'].name,
            'price': record['price']
        } for record in self]

    def dict_app_code(self): 
        return self.app.default_code 

    
  
    
    

    
    
    

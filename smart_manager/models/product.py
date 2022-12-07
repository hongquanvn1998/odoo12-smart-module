
from odoo import models, fields, api 

class ProductTemplate(models.Model):
    _inherit = "product.template"

    software = fields.Boolean('Software')
    app_price_ids =   fields.One2many(
        string='App Price',
        comodel_name='smart_manager.app_price',
        inverse_name='app',
    )
    depend_apps =  fields.Many2many(
        string='Depend Apps',
        comodel_name='product.template',
        relation='product_template_depend_apps_rel',
        column1='main_app_id',
        column2='depend_app_id',
    )
    
    

    


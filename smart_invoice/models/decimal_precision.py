from odoo import models,api 

class DecimalPrecision(models.Model): 
    _inherit = 'decimal.precision'

    @api.model
    def decimal_format(self):
        for item in self:
            item.write({'digits':0}) 
        
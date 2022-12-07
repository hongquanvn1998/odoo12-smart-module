from odoo import models, fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order' 

    app_sale = fields.Boolean(string="App Sale")
    order_register =   fields.Many2one(
        string='Order Register',
        comodel_name='smart_manager.register',
        ondelete='restrict',
    )
    
from odoo import models,fields,api
class Picking(models.Model):
    _inherit = 'stock.picking'
    is_purchase = fields.Boolean(string="Is purchase", compute='compute_is_sale_purchase',store=True)

    @api.multi
    @api.depends('purchase_id')
    def compute_is_sale_purchase(self):
        for order in self:
            if order.purchase_id:
                order.is_purchase = True
            else:
                order.is_purchase = False
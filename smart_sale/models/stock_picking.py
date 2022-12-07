from odoo import models, fields,api

class Picking(models.Model):
    _inherit = 'stock.picking'

    is_sale = fields.Boolean(string="Is sale", compute='compute_is_sale_purchase',store=True)

    @api.multi
    @api.depends('sale_id')
    def compute_is_sale_purchase(self):
        for order in self:
            if order.sale_id:
                order.is_sale = True
            else:
                order.is_sale = False
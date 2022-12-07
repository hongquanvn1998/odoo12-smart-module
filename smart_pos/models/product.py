from odoo import models, fields,api

class ProductProduct(models.Model):
    _inherit = "product.product"

    # traceability_id = fields.Char(string='Traceability')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    pos_enable = fields.Boolean('Can be POS', default=True)
    item_ids = fields.One2many('product.pricelist.item', 'product_tmpl_id', 'Pricelist Items')
    traceability_id = fields.Integer(string='Traceability')

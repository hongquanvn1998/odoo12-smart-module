
from odoo import api, fields, models, _
class StockMove(models.Model):
    _inherit = "stock.move"

    order_line_id = fields.Many2one('pos.order.line', string='Pos order line', readonly=True, copy=False)
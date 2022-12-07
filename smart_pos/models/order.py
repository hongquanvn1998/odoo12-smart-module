from odoo import models,fields,api
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _name = 'pos.order'

    name = fields.Char(string='Pos order name')
    code = fields.Char(string='Pos order code')
    date_order = fields.Datetime(string='Date order')
    company_id = fields.Many2one(
        'res.company',
         string='Company',
    )
    seller_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    qty_total = fields.Integer(string='Quantity total')
    amount_total = fields.Float(string='Amount total')
    discount = fields.Float(string='Pos order discount')
    discount_percent = fields.Float(string ='Pos order  discount percent')
    # khách trả
    amount_paid = fields.Float(string='Amount paid')
    # trả khách
    amount_return = fields.Float(string='Amount return')
    pricelist_ids = fields.Many2many(
        string="Price list",
        comodel_name= "product.pricelist",
        relation="pos_order_pricelist_rel",
        column1="pos_order_id",
        column2="pricelist_id",
    )
    session_id = fields.Many2one(
        'pos.session',
        string='Pos session',
        required=True

    )
    counter_id = fields.Many2one(
        'pos.counter',
        string="Pos counter",
        required=True
    )
    payment_method_ids = fields.Many2many(
        string="Payment method",
        comodel_name="pos.payment.method",
        relation="pos_order_payment_method_rel",
        column1="pos_order_id",
        column2="payment_method_id",
    )
    payment_line_ids=fields.One2many('pos.order.payment.line', 'order_id', string='Order payment Lines', readonly=True, copy=True)
    note= fields.Text(string='Note')
    lines = fields.One2many('pos.order.line', 'order_id', string='Order Lines', readonly=True, copy=True)
    account_move = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    line_ids = fields.One2many(
        string="Order line ids",
        comodel_name="pos.order.line",
        inverse_name="order_id",
    )
    payment_line_ids  = fields.One2many(
        string="Pos order payment line",
        comodel_name="pos.order.payment.line",
        inverse_name="order_id",
    )

    state = fields.Selection(
            [('opened', 'New order'), ('done', 'Posted order')],
            'Status', readonly=True, copy=False, default='opened')

    def default_order_code(self):
        numStr = ''
        id=0
        last_id = self.env['pos.order'].search([], order='id desc', limit=1).id
        if last_id==False:
            id +=1 
        else:
            id=last_id +1
        numStr = "%s" %id
        numStr = numStr.zfill(8)
        return numStr

    def _get_pos_anglo_saxon_price_unit(self, product, partner_id, quantity):
        price_unit = product._get_anglo_saxon_price_unit()
        if product._get_invoice_policy() == "delivery":
            moves = self.filtered(lambda o: o.partner_id.id == partner_id)\
                .mapped('picking_id.move_lines')\
                .filtered(lambda m: m.product_id.id == product.id)\
                .sorted(lambda x: x.date)
            average_price_unit = product._compute_average_price(0, quantity, moves)
            price_unit = average_price_unit or price_unit
        # In the SO part, the entries will be inverted by function compute_invoice_totals
        return - price_unit * quantity

    def _get_price_unit(self, product):
        price_unit = product._get_anglo_saxon_price_unit()
        return - price_unit

class PosOrderLine(models.Model):
    _name = 'pos.order.line'

    name = fields.Char(string='Pos order line name')
    note = fields.Text(string='Note')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    quantity = fields.Integer(string='Quantity')
    price_unit = fields.Float(string='Price unit')
    change_price = fields.Float(string='Change price')
    discount = fields.Float(string ='Pos order line discount')
    discount_percent = fields.Float(string ='Pos order line discount percent')
    price_subtotal = fields.Float(string='Price subtotal')
    order_id = fields.Many2one(
        'pos.order',
        string='Pos order',
    )
class PosOrderPaymentLine(models.Model):
    _name = 'pos.order.payment.line'


    name = fields.Char(string="Name")
    payment_method_id = fields.Many2one(
        string="Payment method",
        comodel_name="pos.payment.method",
        required= True
    )
    journal_id = fields.Many2one(
        string="Account journal",
        comodel_name="account.journal",
        required= True
    )
    amount = fields.Float(string="Amount payment",)
    session_id = fields.Many2one(
        string="Session",
        comodel_name="pos.session",
        required= True
    )
    counter_id = fields.Many2one(
        string="Counter",
        comodel_name="pos.counter",
        required= True
    )
    seller_id = fields.Many2one(
        'res.users',
        string='Seller',
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    order_id = fields.Many2one(
        string="Pos order",
        comodel_name="pos_order",
        required= True
    )
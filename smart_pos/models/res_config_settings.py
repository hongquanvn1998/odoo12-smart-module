
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_tax_id = fields.Many2one('account.tax', string="Default Sale Tax", related='company_id.account_sale_tax_id', readonly=False)
    pos_sales_price = fields.Boolean("Multiple Product Prices", config_parameter='product.group_product_pricelist')
    pos_pricelist_setting = fields.Selection([
        ('percentage', 'Multiple prices per product (e.g. customer segments, currencies)'),
        ('formula', 'Price computed from formulas (discounts, margins, roundings)')
        ], string="POS Pricelists", config_parameter='smart_pos.pos_pricelist_setting')
    # cho phéo đổi điểm hóa đơn
    allow_reward_invoice = fields.Boolean(string="Allow reward invoice", default=True)
    # tỉ lệ đổi tiền = 1 điểm
    reward_point_money_per_point = fields.Integer(string='Reward point money per point',default=100000)
    # cho phép thanh toán bằng điểm
    reward_point_is_point_to_money = fields.Boolean(string="Reward point is point to money")
    # tỉ lệ ? điểm = tiền
    reward_point_point_to_money = fields.Integer(string="Reward point point to money", default=1)
    # tỉ lệ ? itền = điểm
    reward_point_money_to_point = fields.Integer(string="Reward point money to point",default=1000)
    # tích điểm sau bao nhiều lần mua
    reward_point_invoice_count = fields.Integer(string="Reward point invoice count",default=2)
    # tích điểm cho đơn hàng giảm giá
    reward_point_for_discount_invoice = fields.Boolean(string="Reward point for discount invoice", default=False)
    # tích điểm cho hóa đơn thanh toán bằng điểm
    reward_point_for_invoice_using_reward_point = fields.Boolean(string="Reward point for invoice using reward point")
    # tích điểm cho hóa đơn thanh toán bằng voucher
    reward_point_for_invoice_using_voucher = fields.Boolean(string="Reward point for invoice using voucher")
    
    
    @api.onchange('pos_sales_price')
    def _onchange_pos_sales_price(self):
        if not self.pos_sales_price:
            self.pos_pricelist_setting = False
        if self.pos_sales_price and not self.pos_pricelist_setting:
            self.pos_pricelist_setting = 'percentage'

    @api.onchange('pos_pricelist_setting')
    def _onchange_pos_pricelist_setting(self):
        if self.pos_pricelist_setting == 'percentage':
            self.update({
                'group_product_pricelist': True,
                'group_sale_pricelist': True,
                'group_pricelist_item': False,
            })
        elif self.pos_pricelist_setting == 'formula':
            self.update({
                'group_product_pricelist': True,
                'group_sale_pricelist': True,
                'group_pricelist_item': True,
            })
        else:
            self.update({
                'group_product_pricelist': False,
                'group_sale_pricelist': False,
                'group_pricelist_item': False,
            })

    @api.onchange('reward_point_is_point_to_money')
    def set_reward_point_is_point_to_money(self):
        if not self.reward_point_is_point_to_money and self.reward_point_is_point_to_money == False:
            self.reward_point_point_to_money = None
            self.reward_point_money_to_point =None
            self.reward_point_invoice_count = None

    @api.onchange('allow_reward_invoice')
    def set_reward_point_money_per_point(self):
        if not self.allow_reward_invoice and self.allow_reward_invoice == False:
            self.reward_point_money_per_point = None

    @api.constrains('reward_point_money_per_point')
    def check_reward_point_money_per_point(self):
        for item in self:
            if item.allow_reward_invoice:
                if item.reward_point_money_per_point <= 0:
                    raise ValidationError("Tỉ lệ quy đổi điểm thưởng chưa đúng. Số tiền quy đổi ra 1 điểm thưởng phải lớn hơn 0.")
            if item.reward_point_is_point_to_money:
                if item.reward_point_point_to_money <= 0:
                 raise ValidationError("Tỷ lệ thanh toán bằng điểm chưa đúng. Số điểm quy đổi phải lớn hơn 0.")
                if item.reward_point_money_to_point <= 0:
                    raise ValidationError("Tỷ lệ thanh toán bằng điểm chưa đúng. Số tiền quy đổi phải lớn hơn 0.")


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        env= self.env['ir.config_parameter'].sudo()
        res.update(
            allow_reward_invoice=bool(env.get_param('smart_pos.allow_reward_invoice')),
            reward_point_money_per_point=int(env.get_param('smart_pos.reward_point_money_per_point')),
            reward_point_is_point_to_money=bool(env.get_param('smart_pos.reward_point_is_point_to_money')),
            reward_point_point_to_money=int(env.get_param('smart_pos.reward_point_point_to_money')),
            reward_point_money_to_point=int(env.get_param('smart_pos.reward_point_money_to_point')),
            reward_point_invoice_count =int(env.get_param('smart_pos.reward_point_invoice_count')),
            reward_point_for_discount_invoice=bool(env.get_param('smart_pos.reward_point_for_discount_invoice')),
            reward_point_for_invoice_using_reward_point=bool(env.get_param('smart_pos.reward_point_for_invoice_using_reward_point')),
            reward_point_for_invoice_using_voucher=bool(env.get_param('smart_pos.reward_point_for_invoice_using_voucher')),
            pos_sales_price=bool(env.get_param('smart_pos.pos_sales_price')),
            pos_pricelist_setting=env.get_param('smart_pos.pos_pricelist_setting'),

            )
        return res

    def set_values(self):
        env = self.env['ir.config_parameter'].sudo()
        env.set_param('smart_pos.allow_reward_invoice', bool(self.allow_reward_invoice))
        env.set_param('smart_pos.reward_point_money_per_point', int(self.reward_point_money_per_point)),
        env.set_param('smart_pos.reward_point_is_point_to_money', bool(self.reward_point_is_point_to_money)),
        env.set_param('smart_pos.reward_point_point_to_money', int(self.reward_point_point_to_money)),
        env.set_param('smart_pos.reward_point_money_to_point', int(self.reward_point_money_to_point)),
        env.set_param('smart_pos.reward_point_invoice_count', int(self.reward_point_invoice_count)),
        env.set_param('smart_pos.reward_point_for_discount_invoice',bool(self.reward_point_for_discount_invoice)),
        env.set_param('smart_pos.reward_point_for_invoice_using_reward_point',bool(self.reward_point_for_invoice_using_reward_point)),
        env.set_param('smart_pos.reward_point_for_invoice_using_voucher',bool(self.reward_point_for_invoice_using_voucher)),
        env.set_param('smart_pos.pos_sales_price',bool(self.pos_sales_price)),
        env.set_param('smart_pos.pos_pricelist_setting', self.pos_pricelist_setting),

        super(ResConfigSettings, self).set_values()

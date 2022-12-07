from odoo import models,fields,api

class PosRewardPoint(models.Model):
    _name = 'pos.reward.point'

    name =fields.Char(string='Reward No.', compute='_reward_setname', store=False)

    partner_id = fields.Many2one(
    string="Partner",
    comodel_name="res.partner",
    )

    reward_count = fields.Integer(string='Reward Count')

    payment_count = fields.Integer(string='Payment Count')

    points =   fields.Integer(
        string='Reward Points',default=0
    )

    value =  fields.Float(
        string='Value',compute = '_amount_exchange', store=False
    )

    # @api.multi
    @api.depends('points')
    def _amount_exchange(self):
        last_config = self.env['res.config.settings'].search([])[-1]
        point_exchange = last_config['reward_point_money_to_point']/ last_config['reward_point_point_to_money']
        for record in self: 
            record.value = record.points*point_exchange
 
    @api.depends('partner_id') 
    def _reward_setname(self): 
        for record in self: 
            record.name = 'RP-%s' % record.partner_id.id


    

class PosRewardPointHistory(models.Model):
    _name = 'pos.reward.point.history'

    name =fields.Char(string='Reward No.', compute='_reward_setname', store=True)
    counter_id = fields.Many2one(
    string="Counter",
    comodel_name="pos.counter",
    )
    partner_id = fields.Many2one(
    string="Customer",
    comodel_name="res.partner",
    ) 
    transfer_date = fields.Datetime() 
 
    order_id = fields.Many2one(  
    string="Order No.", 
    comodel_name="pos.order")

    reward_point = fields.Integer(string='Reward Points')
    payment_point = fields.Integer(string='Payment Points')
    change_point = fields.Integer(string='Change Points')
    exchange_value = fields.Float(string='Exchange Value') 

    @api.depends('order_id')
    def _reward_setname(self):
        self.name = 'RPH-%s' % self.order_id.code
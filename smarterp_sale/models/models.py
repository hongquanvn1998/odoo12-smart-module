# -*- coding: utf-8 -*-
#Model Register
#Author: Thiep Wong
#Created: 23.6 2019

from odoo import models, fields, api

class smarterp_sale(models.Model):
    _name = 'smarterp_sale.register'
    name = fields.Char()
    partner_id = fields.Many2one('res.partner',string='Partner',required=True)
    email = fields.Char()
    domain = fields.Char()
    modules = fields.Char()
    registered_date = fields.Integer()
    expired_date = fields.Integer()
    order_id = fields.Many2one('sale.order')

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
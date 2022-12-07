# -*- coding: utf-8 -*-

from odoo import models, fields, api
 
class Province(models.Model):
    _name = 'province'

    name = fields.Char(string='Tên tỉnh', required=True)
    code_province = fields.Char(string='Mã tỉnh' , required=True)

class District(models.Model):
    _name = 'district'

    name = fields.Char(string='Tên huyện', required=True)
    code_district = fields.Char(string='Mã Huyện', required=True)
    parent_code = fields.Char(string="Mã tỉnh", required=True)
    depend_province = fields.Many2one('province', string='Thuộc tỉnh', required=True)
     

class Ward(models.Model):
    _name ='ward'

    name = fields.Char(string='Tên xã', required=True)
    code_ward = fields.Char(string="Mã xã", required=True)
    parent_code = fields.Char(string='Mã huyện', required=True)
    depend_district = fields.Many2one('district',string='Thuộc huyện', required=True)
    depend_province = fields.Many2one(related='depend_district.depend_province',string='Thuộc tỉnh', readonly=True, required=True)
# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CompanyAdd(models.Model):
    _inherit= 'res.company'

    province = fields.Many2one('province',string="Tỉnh TP")
    district = fields.Many2one('district', string="Quận Huyện")
    ward = fields.Many2one('ward', string="Xã Phường")
    street_address = fields.Char(string='Tên đường, số nhà...')


    @api.onchange('province')
    def onchange_province(self):
        res = {}
        self.district = False
        parent_code = ''
        if self.province:
            list_district = self.env['district'].search([('parent_code', '=', self.province.code_province)])
            if len(list_district) > 0:
                parent_code = list_district[1].parent_code
            res = {'domain': {'district': [('parent_code', '=', parent_code)]}}
        else:
            res = {}
        return res    
 
    @api.onchange('district')
    def onchange_district(self):
        res = {}
        self.ward = False
        parent_code = ''
        if self.district:
            list_ward = self.env['ward'].search([('parent_code', '=', self.district.code_district)])
            if len(list_ward) > 0:
                parent_code = list_ward[0].parent_code
            res = {'domain': {'ward': [('parent_code', '=', parent_code)]}}
        return res

    
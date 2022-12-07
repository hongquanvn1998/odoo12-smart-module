# -*- coding: utf-8 -*-
from odoo import fields, models, api


class EmployeeAdd(models.Model):
    _inherit= 'hr.employee'

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

    # @api.onchange('tinh')
    # def onchange_tinh(self):
    #     res = {}
    #     self.huyen = False
    #     parent_code = ''
    #     if self.tinh:
    #         list_huyen = self.env['huyen'].search([('parent_code', '=', self.tinh.code_tinh)])
    #         if len(list_huyen) > 0:
    #             parent_code = list_huyen[0].parent_code
    #         res = {'domain': {'huyen': [('parent_code', '=', parent_code)]}}
    #     else:
    #         res = {}
    #     return res

    # @api.onchange('huyen')
    # def onchange_huyen(self):
    #     res = {}
    #     self.xa = False
    #     parent_code = ''
    #     if self.huyen:
    #         list_xa = self.env['xa'].search([('parent_code', '=', self.huyen.code_huyen)])
    #         if len(list_xa) > 0:
    #             parent_code = list_xa[0].parent_code
    #         res = {'domain': {'xa': [('parent_code', '=', parent_code)]}}
    #     return res
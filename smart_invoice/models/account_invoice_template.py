# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountInvoiceTemplate(models.Model):
    _name = 'account.invoice.template'
    name = fields.Char(string='Invoice template', required = True)
    code = fields.Char(string='Invoice template code', required= True)
    image = fields.Binary(string='Invoice template image')
from odoo import models, fields, api
import os
from datetime import datetime


class PaymentMethodJournal(models.Model):
    _inherit = 'account.journal' 
    pos_payment_method = fields.Boolean(string='Is POS payment', default=False)
    pos_payment_method_id = fields.Many2one(string='Payment Method', comodel_name='pos.payment.method')
    
class PosPaymentMethod(models.Model):
    TYPE_SELECTION =[
        ('cash','Cash'),
        ('bank','Bank') ,
        ('point','Point'),
        ('transfer','Transfer'),
    ]
    _name = 'pos.payment.method'
    _inherit = 'mail.thread'
    code = fields.Char(string='Code', required=True, track_visibility='always')
    name = fields.Char(string='Payment Method', required=True,track_visibility='always')
    type = fields.Selection(string='Type', selection=TYPE_SELECTION,default = TYPE_SELECTION[0][0],required=True)
    default_journal_id = fields.Many2one(string='Default Journal', comodel_name='account.journal',track_visibility='always')
    journal_ids =   fields.Many2many(
        string='Journals',
        comodel_name='account.journal',
        inverse_name='pos_payment_method_id',
        domain=[('active', '=', True), ('pos_payment_method', '=', True)],
        track_visibility='always'
    )
    active =  fields.Boolean(
        string='Active',
        default=True,
    )
    def _get_cash(self):
        return self.search([('type', '=', 'cash')])
    @api.onchange('type')
    def get_default_code(self):
        if self.type == 'cash' :
           self.code= 'cash'
        if self.type== 'bank':
            self.code= 'bank'
        if self.type== 'point' :
            self.code = 'point'
        if self.type== 'transfer' :
            self.code = 'transfer'

    def get_list_payment(self, **kw):
        _ids=[]
        if kw['ids']:
            _ids=kw['ids']
        list_payment= ([{
                'payment_id': item.id,
                'payment_name': item.name,
                'payment_code': item.code,
                'payment_type': item.type,
                'payment_journal': [
                    {
                    'id'  : i.id,
                    'name': i.name,
                    'code': i.code
                    }
                    for i in item.journal_ids
             ]
         } for item in self.env['pos.payment.method'].sudo().search([('active', '=', True),('id','in',tuple(_ids))])])
        return list_payment
        
    

    

    
     


    

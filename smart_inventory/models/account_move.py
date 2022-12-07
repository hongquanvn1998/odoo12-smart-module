from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit ='account.move'
    stock_move_id = fields.Many2one('stock.move',string='Stock Move')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    picking_update = fields.Char(string="Credit", compute= "_picking_update_compute", store=True)
    
    @api.one
    @api.depends("move_id")
    def _picking_update_compute(self):
        move_id =  self.move_id
        if (move_id):
            account_move = self.env['account.move'].search([('id','=',move_id.id)])
            if (account_move):
                picking_id = self.env['stock.move'].sudo().search([('id','=',account_move.stock_move_id.id)]).picking_id
                _pickCredit =[]
                _pickDebit=[]
                if (self.credit>0):
                    if (picking_id.credit):
                        _pickCredit =  list(picking_id.credit.split(","))  
                    if (self.account_id.code not in _pickCredit ): 
                        _pickCredit.append(self.account_id.code)
                        picking_id.write({'credit': ','.join(c for c in _pickCredit)})

                if (self.debit>0):
                    if(picking_id.debit):
                        _pickDebit =  list(picking_id.debit.split(","))   
                    if (self.account_id.code not in _pickDebit ): 
                        _pickDebit.append(self.account_id.code)
                        picking_id.write({'debit': ','.join(d for d in _pickDebit)})
        

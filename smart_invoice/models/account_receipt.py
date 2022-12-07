from odoo import api,models,fields, _
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}

 

class AccountReceipt(models.Model):
    _name = "account.receipt"
    # _inherit = 'account.abstract.payment'
    @api.multi
    def get_default(self):
        return  self.env['account.account'].search(['|',('code','=','1111'),('code','=','1121')]).ids

    payment_note = fields.Char(string="Note")
    debit_account_id = fields.Many2one('account.account', string='Account Debit', required=True,domain="['|',('code','=','1111'),('code','=','1121')]")
    credit_account_id = fields.Many2one('account.account', string='Account Credit', required=True)
    payment_amount = fields.Float(string="Amount",required=True)
    payment_id   = fields.Many2one(
        string=u'Payment ID',
        comodel_name='account.payment' 
    )

 

class account_payment(models.Model):
    _inherit = 'account.payment'

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    amount = fields.Monetary(string='Payment Amount', required=True,compute='get_amount_total',store=True)
    # payment_type = fields.Selection(selection_add=[('transfer', 'Internal Transfer')])
    # partner_id = fields.Many2one('res.partner',required=True)
    name_submitter = fields.Char(string='Submitter')
    address_submitter = fields.Char(string='Address',compute='get_address')
    reason = fields.Selection([
        ('0', 'Transfer deposit to cash fund'),
        ('1','Tax refund'),
        ('2','Collect refunds'),
        ('3','Other receivables')
    ], string='Reason Submit', default='3')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    attach = fields.Char(string='Attach')
    date_accouting = fields.Datetime(string='Date Accounting')
    date_vouchers = fields.Datetime(string='Date Vouchers')
    receipt_code = fields.Char(string="Receipt Number", default=lambda self: self._get_next_receipt())
    payment_code = fields.Char(string="Payment Number", default=lambda self: self._get_next_payment())
    receipt_item_ids  =  fields.One2many(
        string=u'Item Ids',
        comodel_name='account.receipt',
        inverse_name='payment_id' 
    )

    receipt_generate = fields.Char(compute = '_create_invoice_receipt')
    # read_number=fields.Char(string='Read Number',compute="reader_number",store=True)

    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        return self.payment_type == 'inbound' and _('PT - %s') % (self.name) or \
                self.payment_type == 'outbound' and _('PC - %s') % (self.name)

    @api.model
    def _get_next_receipt(self):
        sequence = self.env['ir.sequence'].search([('code','=','receipt_next_code')])
        next_code_bill = sequence.get_next_char(sequence.number_next_actual)
        return next_code_bill

    @api.model
    def _get_next_payment(self):
        sequence = self.env['ir.sequence'].search([('code','=','payment_next_code')])
        next_code_invoice = sequence.get_next_char(sequence.number_next_actual)
        return next_code_invoice

    @api.onchange('journal_id')
    def _change_debit(self):
        
        if len(self.invoice_ids) == 1:
            # self.receipt_item_ids.debit_account_id = False
            total_amount = 0
            #self.env['account.account'].search([('code','=',debit_account_code)]).id
            if len(self.receipt_item_ids) == 0:
                result = []
            
                if self.journal_id.type == "cash":
                    debit_account_code = "1111"
                    result.append((0,0,{
                        'payment_note':self.communication,
                        'debit_account_id':self.journal_id.default_debit_account_id ,
                        'credit_account_id': self.destination_account_id.id,
                        'payment_amount':self.amount
                    }))
                else:
                    debit_account_code =  "1121"
                    result.append((0,0,{
                        'payment_note':self.communication,
                        'debit_account_id': self.journal_id.default_debit_account_id ,
                        'credit_account_id': self.destination_account_id.id,
                        'payment_amount':self.amount
                    }))
                self.receipt_item_ids = result
            
            else:
                result = []
                total_amount  = self.amount
                self.receipt_item_ids = False
                if self.journal_id.type == "cash":
                    debit_account_code = "1111"
                    result.append((0,0,{
                        'payment_note':self.communication,
                        'debit_account_id': self.journal_id.default_debit_account_id ,
                        'credit_account_id': self.destination_account_id.id,
                        'payment_amount':total_amount
                    }))
                else:
                    debit_account_code =  "1121"
                    result.append((0,0,{
                        'payment_note':self.communication,
                        'debit_account_id': self.journal_id.default_debit_account_id ,
                        'credit_account_id': self.destination_account_id.id,
                        'payment_amount':total_amount
                    }))
               
                self.receipt_item_ids = result
            
       
        else:
            pass

    @api.model
    @api.depends('receipt_item_ids')
    def _create_invoice_receipt(self):
        print("call in here")
        print(self.id)

    @api.depends("amount")
    def reader_number(self,digit):
        number_read = ('không', 'một', 'hai', 'ba', 'bốn',
                       'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười')
        muoi = 'mươi'
        tram = 'trăm'
        nghin = 'nghìn'
        trieu = 'triệu'
        ty = 'tỷ'
        mot = 'mốt'
        tu = 'tư'
        lam = 'lăm'
        linh = 'linh'
        read_num_null = True
        if (digit>0):
            s = int(digit)
        else: 
            s = int(self.amount)

        def _int(c):
            return ord(c) - ord('0') if c else 0

        def _LT1e2(s):
            if len(s) <= 1:
                return number_read[_int(s)]
            if s[0] == '1':
                ret = number_read[10]
            else:
                ret = number_read[_int(s[0])]
                if muoi:
                    ret += ' ' + muoi
                elif s[1] == '0':
                    ret += ' mươi'
            if s[1] != '0':
                ret += ' '
                if s[1] == '1' and s[0] != '1':
                    ret += mot
                elif s[1] == '4' and s[0] != '1':
                    ret += tu
                elif s[1] == '5':
                    ret += lam
                else:
                    ret += number_read[_int(s[1])]
            return ret

        def _LT1e3(s):
            if len(s) <= 2:
                return _LT1e2(s)
            if s == '000':
                return ''
            ret = number_read[_int(s[0])] + ' ' + tram
            if s[1] != '0':
                ret += ' ' + _LT1e2(s[1:])
            elif s[2] != '0':
                ret += ' ' + linh + ' ' + number_read[_int(s[2])]
            return ret

        def _LT1e9(s):
            if len(s) <= 3:
                return _LT1e3(s)
            if s == '000000' or s == '000000000':
                return ''
            mid = len(s) % 3 if len(s) % 3 else 3
            left, right = _LT1e3(s[:mid]), _LT1e9(s[mid:])
            hang = nghin if len(s) <= 6 else trieu
            if not left:
                if not read_num_null:
                    return right
                else:
                    return number_read[0] + ' ' + hang + ' ' + right
            if not right:
                return left + ' ' + hang
            return left + ' ' + hang + ' ' + right

        def _arbitrary(s):
            if len(s) <= 9:
                return _LT1e9(s)
            mid = len(s) % 9 if len(s) % 9 else 9
            left, right = _LT1e9(s[:mid]), _arbitrary(s[mid:])
            hang = ' '.join([ty] * ((len(s) - mid) // 9))
            if not left:
                if not read_num_null:
                    return right
                elif right:
                    return number_read[0] + ' ' + hang + ' ' + right
                else:
                    return right
            if not right:
                return left + ' ' + hang
            return left + ' ' + hang + ' ' + right 
        _words = _arbitrary(str(s).lstrip('0'))
        return _words[0].upper()+_words[1:]
   
    def _create_receipt_from_invoices(self): 
        for invoice in self.invoice_ids: 
            recept_id = self.env['account.receipt'].create({'payment_note': invoice.invoice_number,'debit_account_id':188 , 'credit_account_id':9 , 'payment_amount': invoice.amount_total, 'payment_id': self.id  })        
            self.env.cr.commit() 

    @api.onchange('partner_id')
    def get_address(self): 
        # result = ''
        # menu = self.env['ir.model.data'].get_object_reference('account_receipt', 'menu_action_currency_form')
        # result += request.httprequest.environ['HTTP_REFERER']
        # result += '#id=' + str(self.id) + '&view_type=form&model=' + request.params["model"] + '&menu_id=' + str(menu[1]) + '&action=' + str(request.params['kwargs']['context']['params']['action'])
        # print ("action_id==============", result)
        if self.partner_id is False:
                pass
        else :  
            self.address_submitter =  self.partner_id.tax_address

    @api.depends('receipt_item_ids')
    def get_amount_total(self):
        # if len(self.invoice_ids) >0:
        #     self.amount = self.payment_difference
        # else:
        if len(self.receipt_item_ids) > 0 :
            for rec in self.receipt_item_ids: 
                    self.amount = int(self.amount) + int(rec.payment_amount)
        else:
            pass
  
    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            result = [] 
            rec['communication'] = invoice['reference'] or invoice['name'] or invoice['number']
            rec['currency_id'] = invoice['currency_id'][0]
            rec['payment_type'] = invoice['type'] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
            rec['partner_id'] = invoice['partner_id'][0]
            rec['amount'] = invoice['residual']
            # result.append((0,0,{
            #     'payment_note':invoice['display_name'],
            #     'debit_account_id':self.env['account.account'].search([('code','=','1121')]).id,
            #     'credit_account_id':invoice['account_id'][0],
            #     'payment_amount':rec['amount']
            # }))
            # rec['receipt_item_ids'] = result
        return rec

    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """

        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                            rec.receipt_code = self.env['ir.sequence'].next_by_code('receipt_next_code')
                            rec.payment_code = False
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                            rec.payment_code = self.env['ir.sequence'].next_by_code('payment_next_code')
                            rec.receipt_code = False
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                            rec.receipt_code = self.env['ir.sequence'].next_by_code('receipt_next_code')
                            rec.payment_code = False
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                            rec.payment_code = self.env['ir.sequence'].next_by_code('payment_next_code')
                            rec.receipt_code = False
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            # print(rec.receipt_item_ids.id)
            if  len(rec.receipt_item_ids) < 1:
                amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = rec._create_payment_entry(amount)
            else:  
                for item in rec.receipt_item_ids:
                    # if len(self.invoice_ids) >0:
                    #     item.debit_account_id.id = self.invoice_ids.invoice_line_ids.account_id.id
                    # else:
                    #     pass
                    amount = item.payment_amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                    move = rec._create_payment_entry_new(amount,item.debit_account_id.id,item.credit_account_id.id)
                    


            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})
        
        aml = self.env['account.move.line'].search([])
        
        for record in aml:
            new=record.payment_id.id
            if int(new) == int(self.id):
                self.env['account.move.line'].search([('payment_id','=',new)]).write({'receipt_code':self.receipt_code})
            else:
                pass
                
        return True
    
    #Create payment with new voucher
    def _create_payment_entry_new(self, amount, account_debit,account_credit):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals_new(account_debit,account_credit,self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        if self.invoice_ids:
            self.invoice_ids.register_payment(counterpart_aml)

        return move


    #Create payment from invoice
    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        self._create_receipt_from_invoices()
        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        if self.invoice_ids:
            self.invoice_ids.register_payment(counterpart_aml)

        return move


    def _get_counterpart_move_line_vals_new(self,account_debit,account_credit, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                    
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name)-2]
        return {
            'name': name,
            'account_id': account_credit or account_debit,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }
    
# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class AccountInvoice(models.Model):
    #_name = "account.invoice"
    _inherit = 'account.invoice'
    invoice_template_id = fields.Many2one(
        'account.invoice.template', string='Invoice template')
    invoice_prefix = fields.Char(string='Invoice prefix code')
    # invoice_number = fields.Integer(string="Invoice Number", default=lambda self: self.env['ir.sequence'].next_by_code('invoice_next_code'))
    invoice_number = fields.Integer(string="Invoice Number", default=lambda self: self._get_next_invoice(),store=True)


    partner_address = fields.Char(string='Vendor address') #Get from tax address of partner
    partner_tax_code = fields.Char(string='Vendor tax code')
    buyer_name = fields.Char(string='Buyer name')
    payment_type  = fields.Selection(
        string=u'Payment type', 
        selection=[('1', 'TM/CK'), ('2', 'Tiền mặt'), ('3', 'Chuyển khoản')],
        default='1',
    )

    #For vendor bill
    tradesman = fields.Char(string='Tradesman')
    description_vendor = fields.Char(string='Description')
    # vendor_bill_number = fields.Integer(string="Vendor Bill Number", default=lambda self: self.env['ir.sequence'].next_by_code('vendor_bill_code'))
    vendor_bill_number = fields.Integer(string="Vendor Bill Number", default=lambda self: self._get_next_bill(), store=True)
    
    # vendor_bill_number = fields.Integer(string="Vendor Bill Number",  store=True)

    #       
    # name = fields.Char(string='Purchase Name', default=lambda self: self._get_next_purchasename(), store=True, readonly=True)
    
    @api.model
    def _get_next_bill(self):
        sequence = self.env['ir.sequence'].search([('code','=','vendor_bill_code')])
        next_code_bill = sequence.get_next_char(sequence.number_next_actual)
        return next_code_bill

    @api.model
    def _get_next_invoice(self):
        sequence = self.env['ir.sequence'].search([('code','=','invoice_next_code')])
        next_code_invoice = sequence.get_next_char(sequence.number_next_actual)
        return next_code_invoice

    @api.onchange('partner_id')
    def _get_partner_info(self):
        if self.partner_id:
            self.partner_tax_code = self.partner_id.vat
            self.partner_address =  self.partner_id.tax_address        
        else:
            pass
    
    @api.model
    def create(self, vals):
        fetch_partner = self.env['res.partner'].search([('id','=',vals['partner_id'])]).supplier
        if fetch_partner==True:
            vals['vendor_bill_number'] = self.env['ir.sequence'].next_by_code('vendor_bill_code')
            vals['invoice_number'] = False
        elif fetch_partner == False:
            vals['invoice_number'] = self.env['ir.sequence'].next_by_code('invoice_next_code')
            vals['vendor_bill_number'] = False

        if not vals.get('journal_id') and vals.get('type'):
            vals['journal_id'] = self.with_context(type=vals.get('type'))._default_journal().id

        onchanges = self._get_onchange_create()
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)
        # bank_account = self._get_default_bank_id(vals.get('type'), vals.get('company_id'))
        # if bank_account and not vals.get('partner_bank_id'):
        #     vals['partner_bank_id'] = bank_account.id

        invoice = super(AccountInvoice, self.with_context(mail_create_nolog=True)).create(vals)

        if any(line.invoice_line_tax_ids for line in invoice.invoice_line_ids) and not invoice.tax_line_ids:
            invoice.compute_taxes()

        return invoice

    # @api.multi
    # def getAccount(self):
    #     self.

    @api.depends("amount_total")
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
        s =0
        if (digit>0):
            s = int(digit)
        else: 
            s = int(self.amount_total)

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




#         select aml.NAME, ai.origin, aml.account_id, aa.NAME, aa.code from account_move_line aml 

# right join
# account_move am  on am.id = aml.move_id
# right join account_invoice ai on ai.move_id = am.id
# left join account_account aa on aa.id = aml.account_id

# order by ai.origin

#         select aml.NAME, ai.origin, aml.account_id, aa.NAME, aa.code,aml.debit,aml.credit from account_move_line aml 

# right join
# account_move am  on am.id = aml.move_id
# right join account_invoice ai on ai.move_id = am.id
# left join account_account aa on aa.id = aml.account_id

# order by ai.origin
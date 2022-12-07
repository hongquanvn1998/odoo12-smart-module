from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError, ValidationError
import time
# from odoo.tests import tagged

class PosSession(models.Model):
    _name = 'pos.session'
    _inherit = 'mail.thread'

    POS_SESSION_STATE = [
        ('opening_control', 'Opening Control'),  # method action_pos_session_open
        ('opened', 'In Progress'),               # method action_pos_session_closing_control
        ('closing_control', 'Closing Session'),  # method action_pos_session_close
    ]

    uuid = fields.Char(string='Session UUID')

    code = fields.Char(string='Session code')
    name = fields.Char(string='Session name',required=True, readonly=True,default='/')
    openned = fields.Datetime(string='Opening Date', readonly=True,track_visibility='always')
    opened_time = fields.Datetime(string='Open Date', readonly=True,track_visibility='always')

    closed = fields.Datetime(string='Closing Date', readonly=True)
    seller_id =  fields.Many2one(
        'res.users', string='User',
        required=True,
        index=True,
        readonly=True,
        )
    state = fields.Selection(
        POS_SESSION_STATE, string='Status',
        required=True, readonly=True,
        index=True, copy=False, default='opening_control', track_visibility='always')
        
    qty_total = fields.Integer(string='Total quantity',compute="_set_total_amount",store=True)
    amount_total = fields.Float(string='Total amount', compute="_set_total_amount",store=True)
    discount_total = fields.Float(string='Total discount',compute="_set_total_amount",store=True)
    amount_paid_total= fields.Float(string='Amount paid',compute="_set_total_amount",store=True)
    amount_return_total = fields.Float(string='Amount return', compute="_set_total_amount", store=True)
    
    config_id = fields.Many2one(
        'pos.counter',
        string='Pos counter',
    )
    price_list_id = fields.Many2one(string='Price list')


    rescue = fields.Boolean(string='Recovery Session',
    help="Auto-generated session for orphan orders, ignored in constraints",
    readonly=True,
    copy=False)

    order_ids = fields.One2many(
        string="Order ids",
        comodel_name="pos.order",
        inverse_name="session_id",
    )

    payment_line_ids = fields.One2many(
        string="Payment line ids",
        comodel_name="pos.order.payment.line",
        inverse_name="session_id",
    )
   
   
    @api.depends('order_ids')
    def _set_total_amount(self):
        for id in self.ids:
            pos_sessions = self.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('rescue', '=', False),
            ('id','=',id)
            ])
          
        if pos_sessions is None:
            raise ValidationError('Pos session not exits!.')
        else:
            self.amount_total =sum(order.amount_total for order in pos_sessions.order_ids)
            self.qty_total = sum(order.qty_total for order in pos_sessions.order_ids)
            self.discount_total = sum(order.discount for order in pos_sessions.order_ids)
            self.amount_paid_total = sum(order.amount_paid for order in pos_sessions.order_ids)
            self.amount_return_total = sum(order.amount_return for order in pos_sessions.order_ids)
                 
    @api.constrains('seller_id', 'state')
    def _check_unicity(self):
        # open if there is no session in 'opening_control', 'opened', 'closing_control' for one user
        if self.search_count([
                ('state', 'not in', ('closed', 'closing_control')),
                ('seller_id', '=', self.seller_id.id),
                ('rescue', '=', False)
            ]) > 1:
            raise ValidationError(("Bạn không thể tạo 2 phiên làm việc cùng lúc!."))

    @api.constrains('config_id')
    def _check_pos_config(self):
        if self.search_count([
                ('state', '!=', ('closed', 'closing_control')),
                ('config_id', '=', self.config_id.id),
                ('rescue', '=', False)
            ]) > 1:
            raise ValidationError(("Bạn phải đóng phiên trước khi mở 1 phiên làm việc mới!. "))

    @api.multi
    def open_frontend_cb(self):
        if not self.ids:
            return {}
        for session in self.filtered(lambda s: s.seller_id.id != self.env.uid):
            raise UserError(("You cannot use the session of another user. This session is owned by %s. "
                              "Please first close this one to use this point of sale.") % session.user_id.name)
        
                    
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url':   '/shop',
        }
        
    @api.multi
    def action_pos_session_closing_control(self):
        self.currency_vn_id = self.env.ref("base.VND").id
        account_move_line = self.env['account.move.line']
        account_move = self.env['account.move']
        # partner_agrolait = self.env.ref("base.res_partner_2")
        self.account_rcv = self.env['account.account']
        self.currency_id = self.env['res.currency'].search([('name','=','VND')]).id
        for session in self:
            if session.config_id is None:
                return ValidationError('Ca giao dịch chưa có hóa đơn nào')
            _pos_order_id = self.env['pos.order'].search([('session_id', '=', session.id)])
            for pos in _pos_order_id:
                _pos_order_line = self.env['pos.order.line'].search([('order_id','=',pos.id)])
                _pos_order_payment_line = self.env['pos.order.payment.line'].search([('order_id', '=', pos.id)])
                move_line_data = []
                if pos.discount > 0:
                    total_new = pos.amount_total + pos.discount
                else:
                    total_new = pos.amount_total
                move_line = {
                    # 'name': 'POS/%s'%(pos.name),
                    'name':'',
                    'debit': total_new,
                    # 'credit': 0.0,
                    'journal_id': session.config_id.journal_id.id,
                    'account_id': self.account_rcv.search([('code','=',131)]).id,
                    # 'currency_id': self.currency_id,
                    'debit_cash_basis':total_new,
                    'partner_id':pos.partner_id.id,
                    'balance_cash_basis':total_new,
                }
                for pos_line in _pos_order_line:
                    vals = {
                        'name': pos_line.product_id.name,
                        # 'debit': 0.0,
                        'journal_id': session.config_id.journal_id.id,
                        'credit': pos_line.price_subtotal,
                        'account_id': self.account_rcv.search([('code','=',5111)]).id,
                        # 'currency_id': self.currency_id,
                        'credit_cash_basis':pos_line.price_subtotal,
                        'product_id':pos_line.product_id.id,
                        'partner_id':pos.partner_id.id,
                        'balance_cash_basis':-pos_line.price_subtotal,
                    }
                    move_line_data.append((0,0,vals))
                move_line_data.append((0,0,move_line))
                move = self.env['account.move'].create({'name': 'POS/%s'%(pos.name),
                    'ref':pos.name,
                    'journal_id': session.config_id.journal_id.id,
                    # 'state':'posted',
                    'company_id': pos.company_id.id,
                    'date':fields.Date.context_today(self),
                    'partner_id':pos.partner_id.id,
                    'amount':total_new,
                    'line_ids': move_line_data,
                    
                })
                move.post()
                for mov in move_line_data:
                    for line_id in move.line_ids:
                        if line_id.account_id.id == self.account_rcv.search([('code','=',131)]).id:
                            line_id.write({
                                'debit_cash_basis':total_new,
                                'balance_cash_basis':total_new,
                            })
                        else:
                            line_id.write({
                                'credit_cash_basis':pos_line.price_subtotal,
                                'balance_cash_basis':-pos_line.price_subtotal,
                            })
                        
                for payment_line in _pos_order_payment_line:
                    vals_amount = {'amount': payment_line.amount,}
                    payment = self.env['account.payment'].create({'payment_type': 'inbound',
                        'payment_method_id': self.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','inbound')]).id,
                        'partner_type': 'customer',
                        'partner_id': payment_line.partner_id.id,
                        'currency_id': self.currency_id,
                        'payment_date': fields.Date.context_today(self),
                        'amount': payment_line.amount,
                        'journal_id': payment_line.journal_id.id,
                        'communication':pos.name,
                        })
                    payment.write(vals_amount)
                    payment.post()
                if pos.amount_return > 0:
                    vals_amount_return = {'amount': pos.amount_return,}
                    payment_return = self.env['account.payment'].create({'payment_type': 'outbound',
                        'payment_method_id': self.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','outbound')]).id,
                        'partner_type': 'customer',
                        'partner_id': pos.partner_id.id,
                        'currency_id': self.currency_id,
                        'payment_date': fields.Date.context_today(self),
                        'amount': pos.amount_return,
                        'journal_id':next((i.default_journal_id.id for i in pos.counter_id.payment_method_ids if i.type == "cash" or i.type == "CASH"), None) ,
                        'communication':pos.name,
                        })
                    payment_return.write(vals_amount_return)
                    payment_return.post()
                if pos.discount > 0 : 
                    vals_discount = {'amount': pos.discount,}
                    payment_discount = self.env['account.payment'].create({'payment_type': 'outbound',
                        'payment_method_id': self.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','outbound')]).id,
                        'partner_type': 'customer',
                        'partner_id': pos.partner_id.id,
                        'currency_id': self.currency_id,
                        'payment_date': fields.Date.context_today(self),
                        'amount': pos.discount,
                        'journal_id': self.env['account.journal'].search(['|',('code','=','disc'),('code','=','DISC')])[0].id,
                        'communication':pos.name,
                        })
                    payment_discount.write(vals_discount)
                    payment_discount.post()
            _pos_order_id.sudo().write({'state':'done'})
            session.write({'state': 'closing_control', 'closed': fields.Datetime.now()})
            # if not session.config_id.cash_control:
            #     session.action_pos_session_close()\

    def action_pos_session_closing_control_mobile(self,**kw):
        self.currency_vn_id = self.env.ref("base.VND").id
        account_move_line = self.env['account.move.line']
        account_move = self.env['account.move']
        load_session = self.env['pos.session'].search([('id','=',kw.get('session_id'))])
        # partner_agrolait = self.env.ref("base.res_partner_2")
        self.account_rcv = self.env['account.account']
        self.currency_id = self.env['res.currency'].search([('name','=','VND')]).id
        for session in load_session:
            if session.config_id is None:
                data = {
                'message': 'Ca giao dịch chưa có hóa đơn nào',
                'code': 400,
                'status' :False
                    }
                return data
            _pos_order_id = self.env['pos.order'].search([('session_id', '=', session.id)])
            for pos in _pos_order_id:
                _pos_order_line = self.env['pos.order.line'].search([('order_id','=',pos.id)])
                _pos_order_payment_line = self.env['pos.order.payment.line'].search([('order_id', '=', pos.id)])
                move_line_data = []
                if pos.discount > 0:
                    total_new = pos.amount_total + pos.discount
                else:
                    total_new = pos.amount_total
                move_line = {
                    # 'name': 'POS/%s'%(pos.name),
                    'name':'',
                    'debit': total_new,
                    # 'credit': 0.0,
                    'journal_id': session.config_id.journal_id.id,
                    'account_id': self.account_rcv.search([('code','=',131)]).id,
                    # 'currency_id': self.currency_id,
                    'debit_cash_basis':total_new,
                    'partner_id':pos.partner_id.id,
                    'balance_cash_basis':total_new,
                }
                for pos_line in _pos_order_line:
                    vals = {
                        'name': pos_line.product_id.name,
                        # 'debit': 0.0,
                        'journal_id': session.config_id.journal_id.id,
                        'credit': pos_line.price_subtotal,
                        'account_id': self.account_rcv.search([('code','=',5111)]).id,
                        # 'currency_id': self.currency_id,
                        'credit_cash_basis':pos_line.price_subtotal,
                        'product_id':pos_line.product_id.id,
                        'partner_id':pos.partner_id.id,
                        'balance_cash_basis':-pos_line.price_subtotal,
                    }
                    move_line_data.append((0,0,vals))
                move_line_data.append((0,0,move_line))
                move = self.env['account.move'].create({'name': 'POS/%s'%(pos.name),
                    'ref':pos.name,
                    'journal_id': session.config_id.journal_id.id,
                    # 'state':'posted',
                    'company_id': pos.company_id.id,
                    'date':fields.Date.context_today(self),
                    'partner_id':pos.partner_id.id,
                    'amount':total_new,
                    'line_ids': move_line_data,
                    
                })
                move.post()
                for mov in move_line_data:
                    for line_id in move.line_ids:
                        if line_id.account_id.id == self.account_rcv.search([('code','=',131)]).id:
                            line_id.write({
                                'debit_cash_basis':total_new,
                                'balance_cash_basis':total_new,
                            })
                        else:
                            line_id.write({
                                'credit_cash_basis':pos_line.price_subtotal,
                                'balance_cash_basis':-pos_line.price_subtotal,
                            })
                        
                for payment_line in _pos_order_payment_line:
                    vals_amount = {'amount': payment_line.amount,}
                    payment = self.env['account.payment'].create({'payment_type': 'inbound',
                        'payment_method_id': self.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','inbound')]).id,
                        'partner_type': 'customer',
                        'partner_id': payment_line.partner_id.id,
                        'currency_id': self.currency_id,
                        'payment_date': fields.Date.context_today(self),
                        'amount': payment_line.amount,
                        'journal_id': payment_line.journal_id.id,
                        'communication':pos.name,
                        })
                    payment.write(vals_amount)
                    payment.post()
                if pos.amount_return > 0:
                    vals_amount_return = {'amount': pos.amount_return,}
                    payment_return = self.env['account.payment'].create({'payment_type': 'outbound',
                        'payment_method_id': self.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','outbound')]).id,
                        'partner_type': 'customer',
                        'partner_id': pos.partner_id.id,
                        'currency_id': self.currency_id,
                        'payment_date': fields.Date.context_today(self),
                        'amount': pos.amount_return,
                        'journal_id':next((i.default_journal_id.id for i in pos.counter_id.payment_method_ids if i.type == "cash" or i.type == "CASH"), None) ,
                        'communication':pos.name,
                        })
                    payment_return.write(vals_amount_return)
                    payment_return.post()
                if pos.discount > 0 : 
                    vals_discount = {'amount': pos.discount,}
                    payment_discount = self.env['account.payment'].create({'payment_type': 'outbound',
                        'payment_method_id': self.env['account.payment.method'].search([('code','=','manual'),('payment_type','=','outbound')]).id,
                        'partner_type': 'customer',
                        'partner_id': pos.partner_id.id,
                        'currency_id': self.currency_id,
                        'payment_date': fields.Date.context_today(self),
                        'amount': pos.discount,
                        'journal_id': self.env['account.journal'].search(['|',('code','=','disc'),('code','=','DISC')])[0].id,
                        'communication':pos.name,
                        })
                    payment_discount.write(vals_discount)
                    payment_discount.post()
            _pos_order_id.sudo().write({'state':'done'})
            try:
                session.write({'state': 'closing_control', 'closed': fields.Datetime.now()})
            except Exception as e:
                data = {
                'message': 'Lỗi hóa đơn: %s'%e,
                'code': 400,
                'status' :False
                    }
                return data
        data = {
                'message': 'Đóng quầy thành công',
                'code': 200,
                'status' :True
                    }
        return data

  
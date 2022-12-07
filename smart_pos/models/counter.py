from odoo import models, fields, api,_
import datetime
from odoo.http import request
import datetime
from odoo.exceptions import UserError, ValidationError
import uuid

# Manager counter of POS
class PosCounter (models.Model):
    _name = "pos.counter"
    _inherit = 'mail.thread'

    name = fields.Char(string='Name',required=True, track_visibility='always')
    code = fields.Char(string='Code',track_visibility='always')
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required= True
    )
    iot_gateway = fields.Char(string='IoT gateway')

    barcode_scanner = fields.Boolean(string='Barcode scanner')
    electronic_scale = fields.Boolean(string='Electronic scale')
    cash_drawer = fields.Boolean(string='Cash drawer')
    price_displayer = fields.Boolean(string='Price displayer')


    pricelist_ids = fields.Many2many(
        string="Price list",
        comodel_name= "product.pricelist",
        relation="pos_counter_pricelist_rel",
        column1="pos_counter_id",
        column2="pricelist_id",
        required=True,
        track_visibility='always'

    )
        
    payment_method_ids = fields.Many2many(
        string='Available Payment Methods',
        comodel_name=  'pos.payment.method',
        relation='pos_config_payment_method_rel',
        column1='pos_config_id',
        column2='payment_method_id',
        domain="[('type', 'in', ['bank', 'cash','point','transfer'])]",
        required=True,
    )
     
    journal_id = fields.Many2one(
        'account.journal', string='Journal ',
        domain=[('type', '=', ['sale'])],
        required=True,
        track_visibility='always'

        )

    session_ids = fields.One2many(
        string="session_ids",
        comodel_name="pos.session",
        inverse_name="config_id",
        track_visibility='always'
    )
    current_session_id = fields.Many2one('pos.session', compute='_compute_current_session', string="Current Session")
    current_session_state = fields.Char(compute='_compute_current_session')
    pos_session_state = fields.Char(compute='_compute_current_session_user')


    stock_picking_type_id = fields.Many2one(
    string="Stock picking type",
    comodel_name="stock.picking.type",
    required=True,
    domain="[('code','=','outgoing')]",
    track_visibility='always'
    )

    pos_session_username = fields.Char(compute='_compute_current_session_user')
    pos_session_duration = fields.Char(compute='_compute_current_session_user')
    last_session_closing_cash = fields.Float(compute='_compute_last_session')
    last_session_closing_date = fields.Date(compute='_compute_last_session')

    order_code = fields.Char(string='Order code print',required=True)


    @api.onchange('name')
    def onchage_code_default(self):
        numStr = ''
        id=0
        try:
            last_id = self.search([], order='id desc', limit=1).ids
            if len(last_id)==0  or last_id[0] ==0:
                id =1 
            if len(last_id) > 0:
                id +=last_id[0] +1
            numStr = "%s" %id
            numStr = numStr.zfill(8)
            self.code = ('PC-%s' % (numStr))
        except:
            pass

    @api.multi
    def open_ui(self):
        """ open the pos interface """
        self.ensure_one()
        # check all constraints, raises if any is not met
        # self._validate_fields(self._fields)
        res_config_settings =self.sudo().env['res.config.settings'].sudo().get_values()
        if res_config_settings['allow_reward_invoice']==True and res_config_settings['reward_point_money_per_point'] <=0:
           raise ValidationError('Tỉ lệ quy đổi điểm thưởng chưa đúng. Số tiền quy đổi ra 1 điểm thưởng phải lớn hơn 0!.')
        if res_config_settings['reward_point_is_point_to_money'] ==True and res_config_settings['reward_point_point_to_money'] <=0 and res_config_settings['reward_point_money_to_point'] <=0 and res_config_settings['reward_point_invoice_count']<=0:
           raise ValidationError('Cấu hình cho phép thanh toán bằng điểm chưa đúng!.')
      
        return {
            'type': 'ir.actions.act_url',
            'url':   '/shop',
            'target': 'self',
        }
    def default_session_name(self):
        x = datetime.datetime.now()
        date='%s/%s/%s' %(x.year,x.month,x.day)
        result = ''
        last_session = self.env['pos.session'].search([], order="id desc", limit=1).id
        if last_session==False:
            last_session = 1
        else:
            last_session +=1
        result= '%s/%s/%s'  %(self.name,date,last_session)
        return result

    def default_session_code(self):
        numStr = ''
        id=0
        last_id = self.env['pos.session'].search([], order='id desc', limit=1).id
        if last_id==False:
            id +=1 
        else:
            id=last_id +1
        numStr = "%s" %id
        numStr = numStr.zfill(8)
        numStr = 'PS-%s' % (numStr)
        return numStr

    @api.multi
    def open_session_cb(self):
        """ new session button

        create one if none exist
        access cash control interface if enabled or start a session
        """
        self.ensure_one()
        if not self.current_session_id:
            self.current_session_id = self.env['pos.session'].create({
                'seller_id': self.env.uid,
                'config_id': self.id,
                'state': 'opened',
                'name': self.default_session_name(),
                'code' :self.default_session_code(),
                'openned': fields.Datetime.now()
                
            })
            if self.current_session_id.state == 'opened':
                return self.open_ui()
            return self._open_session(self.current_session_id.id)
        return self._open_session(self.current_session_id.id)

    
    #ThiepWong added. Using this method changed for old
    def open_new_session(self):
        _uuid = uuid.uuid4().hex
        self.current_session_id = self.env['pos.session'].create({
                'seller_id': self.env.uid,
                'config_id': self.id,
                'state': 'opened',
                'name': self.default_session_name(),
                'code' :self.default_session_code(),
                'uuid' : _uuid,
                'openned': fields.Datetime.now() 
            })
        return    {
            'name': 'Open Shop',
            'type': 'ir.actions.act_url',
            'url': '/shop?swift_code=%s' % _uuid,
            'target': 'self',
        }
        
    def continue_session(self):
        session = self.env['pos.session'].search([('config_id','=',self.id),('seller_id','=',self.env.uid),('state','=','opened')])
        if not session:
            raise ValidationError(_("Không có phiên làm việc nào đang hoạt động!"))

        return    {
            'name': 'Open Shop',
            'type': 'ir.actions.act_url',
            'url': '/shop?swift_code=%s' % session.uuid,
            'target': 'self',
        }
    
    def open_new_session_mobile(self):
        _uuid = uuid.uuid4().hex
        self.current_session_id = self.env['pos.session'].create({
                'seller_id': self.env.uid,
                'config_id': self.id,
                'state': 'opened',
                'name': self.default_session_name(),
                'code' :self.default_session_code(),
                'uuid' : _uuid,
                'openned': fields.Datetime.now() 
            })
        return {'swift_code': self.current_session_id.uuid}

    def continue_session_mobile(self):
        session = self.env['pos.session'].search([('config_id','=',self.id),('seller_id','=',self.env.uid),('state','=','opened')])
        if not session:
            raise ValidationError(_("Không có phiên làm việc nào đang hoạt động!"))

        return   {'swift_code': session.uuid}
 
         

    @api.multi
    def open_existing_session_cb(self):
        """ close session button

        access session form to validate entries
        """
        self.ensure_one()
        return self._open_session(self.current_session_id.id)

    @api.depends('session_ids')
    def _compute_current_session(self):
        for pos_config in self:
            session = pos_config.session_ids.filtered(lambda r: r.seller_id.id == self.env.uid and \
                not r.state == 'closing_control' and \
                not r.rescue)
            # sessions ordered by id desc
            pos_config.current_session_id = session and session[0].id or False
            pos_config.current_session_state = session and session[0].state or False

    def _open_session(self, session_id):
        return {
            'name': 'Session',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.session',
            'res_id': session_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    @api.depends('session_ids')
    def _compute_current_session_user(self):
        for pos_config in self:
            session = pos_config.session_ids.filtered(lambda s: s.state in ['opened'] and not s.rescue)
            if session:
                pos_config.pos_session_username = session[0].seller_id.name
                pos_config.pos_session_state = session[0].state
                pos_config.pos_session_duration = (
                    datetime.datetime.now() - session[0].openned
                ).days if session[0].openned else 0
            else:
                pos_config.pos_session_username = False
                pos_config.pos_session_state = False
                pos_config.pos_session_duration=0


    @api.depends('session_ids')
    def _compute_last_session(self):
        PosSession = self.env['pos.session']
        for pos_config in self:
            session = PosSession.search_read(
                [('config_id', '=', pos_config.id), ('state', '=', 'closing_control')],
                order="closed desc", limit=1)
            if session:
                pos_config.last_session_closing_cash = session[0]['amount_total']
                pos_config.last_session_closing_date = session[0]['closed'].date()
            else:
                pos_config.last_session_closing_cash = 0
                pos_config.last_session_closing_date = False

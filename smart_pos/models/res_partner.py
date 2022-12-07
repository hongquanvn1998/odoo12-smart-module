from odoo import api,models,fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    birthday = fields.Date(string="Ngày sinh")
    facebook = fields.Char(string="Facebook")

    def _get_customer_code(self):
        numStr = ''
        id=0
        last_id = self.env['res.partner'].search([], order='id desc', limit=1).id
        if last_id==False:
            id +=1 
        else:
            id=last_id +1
        numStr = "%s" %id
        numStr = numStr.zfill(8)
        numStr = 'KH-%s' % (numStr)
        return numStr

    @api.model
    def create(self, vals):
        if vals.get('customer_code', 'New') == 'New':
            vals['customer_code'] = self.env['ir.sequence'].next_by_code(
                'res.partner') or 'New'
        result = super(ResPartner, self).create(vals)
        return result

    customer_code = fields.Char(string='Mã khách hàng' ,readonly=True, required=True, copy=False, default='New')

    def get_role(self,**kw):
        get_user = {}
        uid = self.env.uid
        current_user = self.env['res.users'].search([('id','=',uid)])

        get_user['is_admin'] = True if self.env.ref("smart_pos.group_pos_admin").id in current_user.groups_id.ids else False
        get_user['is_manager'] = True if self.env.ref("smart_pos.group_pos_manager").id in current_user.groups_id.ids else False
        get_user['is_seller'] = True if self.env.ref("smart_pos.group_pos_user").id in current_user.groups_id.ids else False
        
        get_user['id'] = current_user.id
        get_user['name'] = current_user.display_name
        get_user['mobile'] = current_user.mobile
        get_user['email'] = current_user.email
        get_user['partner_id'] = current_user.partner_id.id

        return get_user
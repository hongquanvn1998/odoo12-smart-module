from odoo import _,api,models,fields

import logging

_logger = logging.getLogger(__name__)

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def create_user(self):
        self.env.cr.execute('select * from smart_init_apps order by id asc limit 1')

        get_user = self.env.cr.fetchone()
        if get_user != None:
            values = {
                'name': get_user[1],
                'login': get_user[2],
                'email': get_user[3],
                'password': get_user[4],
                'notification_type': 'inbox',
            }
            user = super(Users, self).create(values)
            group_erp_manager = self.env.ref('base.group_erp_manager')
            if get_user[5]:
                group_pos_admin = self.env.ref('smart_pos.group_pos_admin')
                group_pos_admin.users = [(4, user.id)]
            group_erp_manager.users = [(4, user.id)]
            cron = self.env.ref('smart_init.ir_cron_create_user')
            self.env.cr.execute('DELETE FROM smart_init_apps where id = %s' % get_user[0])
            self.env.cr.commit()
            # self.env.cr.execute('UPDATE ir_cron SET active = false where id = %s' % cron.id)
            # self.env.cr.commit()
            return user
        return _logger.info('***************************Nothing*************************************')
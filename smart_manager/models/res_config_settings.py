from odoo import api,models,_ ,fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_admin = fields.Char(string='Admin Account')
    create_invoice = fields.Boolean(string='Create Invoice')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        env= self.env['ir.config_parameter'].sudo()
        res.update(
            create_invoice = bool(env.get_param('smart_manager.create_invoice')),
            user_admin = env.get_param('smart_manager.user_admin'),

            )
        return res

    def set_values(self):
        env = self.env['ir.config_parameter'].sudo()
        env.set_param('smart_manager.create_invoice', bool(self.create_invoice))
        env.set_param('smart_manager.user_admin', self.user_admin),

        super(ResConfigSettings, self).set_values()

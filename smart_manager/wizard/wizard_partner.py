from odoo import models,fields,api,_

class ReportPartnerWizard(models.TransientModel):
    _name = 'report.partner.wizard'

    start_date = fields.Date(string='Date Start',default=fields.Date.today)
    end_date = fields.Date(string='Date end',default=fields.Date.today)

    filter_partner = fields.Many2one(string='Partner', comodel_name='res.partner',domain=['&',('active','=',True),('customer','=',True)])

    def set_list_params(self):
        params = {
            'start_date':self.start_date,
            'end_date':self.end_date,
            'partner_id':self.filter_partner,
        }
        return self.env['report.register.partner'].reload_data(params)
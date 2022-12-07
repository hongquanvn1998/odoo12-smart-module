from odoo import fields,models,api,_

class ReportCustomerWizard (models.TransientModel):
    _name = 'report.customer.wizard'

    start_date = fields.Date(string='Date start',default=fields.Date.today)
    end_date = fields.Date(string='Date end',default=fields.Date.today)

    filter_customer = fields.Many2one(string='Customer', comodel_name='res.partner',domain=['&',('active','=',True),('customer','=',True)])

    def set_list_params(self):
        params = {
            'start_date':self.start_date,
            'end_date':self.end_date,
            'customer_id':self.filter_customer,
        }
        return self.env['report.register.customer'].reload_data(params)
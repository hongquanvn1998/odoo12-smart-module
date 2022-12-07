from odoo import models,fields,api,_
# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
import calendar
import time
from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError, UserError, RedirectWarning
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools import date_utils

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner' 
    tax_address = fields.Char(string='Tax address')

class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company' 
    tax_address = fields.Char(string='Tax address')

    # @api.model
    # def setting_init_fiscal_year_action(self):
    #     """ Called by the 'Fiscal Year Opening' button of the setup bar."""
    #     company = self.env.user.company_id
    #     company.create_op_move_if_non_existant()
    #     new_wizard = self.env['account.financial.year.op'].create({'company_id': company.id})
    #     if new_wizard:
    #         new_wizard.opening_date = new_wizard.opening_date + timedelta(days=1)
    #     else:
    #         pass
    #     # datetime.strptime(new_wizard.opening_date, '%Y-%m-%d')+relativedelta(days =+ 1)
    #     # new_wizard.opening_date.replace(month=self.fiscalyear_last_month, day=self.fiscalyear_last_day) + timedelta(days=1)
    #     view_id = self.env.ref('account.setup_financial_year_opening_form').id

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Fiscal Year'),
    #         'view_mode': 'form',
    #         'res_model': 'account.financial.year.op',
    #         'target': 'new',
    #         'res_id': new_wizard.id,
    #         'views': [[view_id, 'form']],
    #     }

    # @api.model
    # def create_op_move_if_non_existant(self):
    #     """ Creates an empty opening move in 'draft' state for the current company
    #     if there wasn't already one defined. For this, the function needs at least
    #     one journal of type 'general' to exist (required by account.move).
    #     """
    #     self.ensure_one()
    #     if not self.account_opening_move_id:
    #         default_journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.id)], limit=1)

    #         if not default_journal:
    #             raise UserError(_("Please install a chart of accounts or create a miscellaneous journal before proceeding."))

    #         today = datetime.today().date()
    #         opening_date = today.replace(month=self.fiscalyear_last_month, day=self.fiscalyear_last_day)
    #         # opening_date1 = today.replace(month=self.fiscalyear_last_month, day=self.fiscalyear_last_day)
    #         if opening_date > today:
    #             opening_date = opening_date + relativedelta(years=-1)

    #         self.account_opening_move_id = self.env['account.move'].create({
    #             'name': _('Opening Journal Entry'),
    #             'company_id': self.id,
    #             'journal_id': default_journal.id,
    #             'date': opening_date,
    #         })


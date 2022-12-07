from odoo import api,models,fields
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import xlwt
import xlsxwriter
import unicodedata
import base64
import io
from io import StringIO
import csv
import babel.numbers
import decimal
from collections import Counter
from odoo.exceptions import ValidationError

class AllBalanceSheetView(models.AbstractModel):
    _name='report.smart_invoice.balance_sheet_display'

#Modified by Thiep Wong 30.11/2019
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        company_id =data['form']['company']
        account_level = data['form']['account_level']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= '%s %s' % (end_date, '23:59:59')
        balance_2_side = data['form']['balance_2_side'] 
        
        docs=[]
        self.env.cr.execute(
                """
                select  (case when opening.code is not null then opening.code when opening.code is null then incurred.code end ) code , 
                (case when opening.name is not null then opening.name when opening.name is null then incurred.name end ) account_name , 
                COALESCE (opening.debit, 0) opening_debit,  
                COALESCE (opening.credit,0) opening_credit,
                COALESCE (incurred.debit,0) incurred_debit,
                COALESCE (incurred.credit,0) incurred_credit,

                (select max(debit) from unnest(array[0, COALESCE (opening.debit,0)+COALESCE (incurred.debit,0)- COALESCE (incurred.credit,0) - COALESCE (opening.credit,0)]) debit  )  close_debit,
                (select max(credit) from unnest(array[0,COALESCE (opening.credit,0)+COALESCE (incurred.credit,0)- COALESCE (incurred.debit,0) - COALESCE (opening.debit,0)]) credit  )  close_credit  

                from

                (select  
                aa.code,aa.name, sum(aml.debit) debit, sum(aml.credit) credit
                from  
                account_move_line aml   
                left join account_account aa on aa.id = aml.account_id 
                where  
                aml.company_id = %s
                and
                aml.DATE <  %s
                group by aa.code, aa.name 
                order by aa.code ) opening

                full join

                (
                select 

                aa.code,aa.name, sum(aml.debit) debit, sum(aml.credit) credit
                from 

                account_move_line aml   
                left join account_account aa on aa.id = aml.account_id

                where 


                aml.company_id = %s
                and aml.Date >= %s and aml.Date <= %s
                group by aa.code,aa.name 
                order by aa.code ) incurred 
                on opening.code = incurred.code 
                       """ ,(company_id,start_date,company_id,start_date,end_date)
                    )
        ac_balance = self.env.cr.fetchall() 
        
        if (account_level == '1'):
            pass
        if (account_level == '2'):
            pass 
        if (account_level=='3'):
            for record in ac_balance:
                docs.append({
                    'code':record[0],
                    'account_name':record[1],
                    'o_debit':record[2],
                    'o_credit':record[3],
                    'i_debit':record[4],
                    'i_credit':record[5],
                    'c_debit':record[6],
                    'c_credit':record[7],
                    })
            pass
 
       
        return {
            'doc_ids': self.ids, 
            'data': data['form'],
            'docs': docs,
            'start_date':start_date,
            'end_date':end_date,
        }

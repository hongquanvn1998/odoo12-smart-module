from odoo import models,api
class CashLedger(models.Model):
    _name = 'cash.ledger'

    @api.model
    def _get_report_values(self,docids,data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        end_date= end_date + ' 23:59:59'
        filter_account = data['form']['filter_account']
        company_id= data['form']['company_id']
        account_ids= tuple(filter_account)
        if len(account_ids) == 0 :
                docs = []
                return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_start': start_date,
                'date_end': end_date,
                'docs': docs,
            }
                pass
        else :

        #   str
            self.env.cr.execute(
            """
	    select 
			incurred.voucher_date,
			incurred.accounting_date,
			incurred.aml_name as  vourcher_name, 
		(case 
		 when opening.code is not null then opening.code else incurred.code
		 end) code,
		 		incurred.counter_part_code, 
		  (CASE 
             WHEN opening.debit is not null
             THEN opening.debit
             ELSE 0
             END)
             AS opening_debit,

               (CASE 
             WHEN incurred.debit is not null
             THEN incurred.debit
             ELSE 0
             END)
             AS  opening_credit,
			  (CASE 
             WHEN incurred.debit is not null
             THEN incurred.debit
             ELSE 0
             END)
             AS incurred_debit,

               (CASE 
             WHEN incurred.credit is not null
             THEN incurred.credit
             ELSE 0
             END)
             AS  incurred_credit,
			incurred .rp_name
			
		from ( select 
            aa.code,
          (CASE 
				WHEN SUM(aml.credit) is not null
				THEN SUM(aml.credit)
				ELSE 0
				END) AS credit,
			 (CASE 
				WHEN SUM(aml.debit) is not null
				THEN SUM(aml.debit)
				ELSE 0
			END) AS debit
            from account_move_line aml
            left join  account_move am
            on aml.move_id = am.id
            left join account_account aa
            on aa.id= aml.account_id
            left join account_journal aj
            on aml.journal_id = aj.id
           where  aml.date <  %s and  aa.code  in %s
           and aml.company_id =%s
            group by aa.code)   opening 
			
			full join
			
			( select 
        aml.date as accounting_date,
        aml.date_maturity as voucher_date,
        aml.name vourcher_name, 
        aa.code,
        ( select array_agg(ab.code) from account_move_line a left join account_account ab on ab.id = a.account_id 
        where a.move_id = aml.move_id and a.account_id !=aml.account_id  group by ab.code limit 1) counter_part_code,
        aml.credit,
        aml.name as aml_name,
        aml.debit,
        aa.name, 
        rp.name as rp_name
        from account_move_line aml

        left join account_move am on am.id = aml.move_id 
        left join account_account aa on aa.id = aml.account_id
        left join account_move_line amls on amls.move_id = aml.move_id
        left join res_partner rp
        on aml.partner_id = rp.id
        where
        aa.code in %s
        and
        aml.date >=  %s and aml.date <= %s
        and aml.company_id =%s

        group by aa.code,aa.name, aml.debit, aml.credit,aml.name,aml.date,counter_part_code,voucher_date,rp.name

        order by aa.code, aml.date
        ) incurred
        on incurred.code = opening.code
             """
                    ,(start_date,account_ids,company_id,account_ids,start_date,end_date,company_id)
                )
        self.account_cash = self.env.cr.fetchall() 
        docs = []
        code= ''
        _item=[]
        ob=0
        record = []
        group = []
        _index =0 
        for item in  self.account_cash:
            _index += 1
            if item[3] != code:
                if len(group)>0:
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
                group = []
                group.append(item)
                code = item[3]
                ob=item[5]-item[6]
                if _index >= len(self.account_cash):
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
            else:
                group.append(item)
                if _index >= len(self.account_cash):
                    docs.append({
                    'items': group,
                    'code' :code,
                    'ob':ob
                            })
    
          
        return{
                'doc_ids':data['ids'],
                'doc_model':data['model'],
                'start_date':start_date,
                'end_date':end_date,
                'docs':docs,
            }
    @staticmethod
    def to_array(str):
        list = []
        for value in str:
                try:
                    list.append(int(value))
                except ValueError:
                    continue
        return list
    @staticmethod
    def to_tupe(str,order):
        tupe=[]
        length = len(str) -1
        for record in str[order:length].split(","):
                if record.strip().isdigit() == True:
                    tupe.append(record.strip())
        return tupe
                

         
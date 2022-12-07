from odoo import fields,models,api,tools,_

class ReportRegisterCustomer(models.Model):
    _name = 'report.register.customer'
    _auto = False

    STATE_SELECTION = [( 'draft',_('Draft')),( 'registered',_('Registered')), ('verifying', _('Verifying')), ('verified', _('Verified')),
    ('initialing',_('Initialing')), ('activated', _('Activated')), ('expired', _('Expired')), ('cancelled', _('Cancelled'))]

    customer_name = fields.Char(string='Customer Name')
    date = fields.Datetime(string='Date')
    app_name = fields.Char(string='App Name')
    app_price = fields.Float(string='App price')
    register_quantity = fields.Char(string='Register Quantity')
    customer_id = fields.Many2one(comodel_name='res.partner',string='Customer Id')
    state =   fields.Selection(
        string='Status',
        selection= STATE_SELECTION,
    )

    def reload_data(self,kw):
        start_date = kw['start_date']
        end_date = kw['end_date']
        customer_id = kw['customer_id']

        res_partner = 'rp.name customer_name,' if customer_id else 'smr.partner_name customer_name,' 

        sql = """
            CREATE OR REPLACE VIEW  %s AS           
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            ap.name app_name,
            ap.price app_price,
            pp.name register_quantity,    
            smr.register_date date,
            smr.state state,
            %s
            rp.id customer_id

            FROM smart_manager_register smr 
            left join res_partner rp on smr.partner = rp.id
            left join smart_manager_register_app_price_rel pm on smr.id = pm.register_id
            left join smart_manager_app_price ap on pm.price_id = ap.id
            left join smart_manager_payment_period pp on ap.period = pp.id
                 
            WHERE 
            smr.register_date >= '%s 00:00:00' and smr.register_date <= '%s 23:59:59'
            AND smr.state NOT IN('draft','expired')
        """%(self._table,res_partner,start_date,end_date)

        if customer_id:
            sql += """
            AND smr.partner = %s
            """%customer_id.id
        sql += """
        ORDER BY smr.register_date ASC
        """
        if 'vi_VN' in self._context.values():
            name = 'Báo cáo theo khách hàng'
        else:
            name = 'Report customer'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.register.customer' ,
            "context":{'start_date':start_date, 'end_date':end_date}
                }
from odoo import fields,models,api,tools,_

class ReportRegisterPartner(models.Model):
    _name = 'report.register.partner'
    _auto = False

    STATE_SELECTION = [( 'draft',_('Draft')),( 'registered',_('Registered')), ('verifying', _('Verifying')), ('verified', _('Verified')),
    ('initialing',_('Initialing')), ('activated', _('Activated')), ('expired', _('Expired')), ('cancelled', _('Cancelled'))]

    partner_name = fields.Char(string='Partner Name')
    date = fields.Datetime(string='Date')
    app_name = fields.Char(string='App Name')
    app_price = fields.Float(string='App price')
    register_quantity = fields.Char(string='Register Quantity')
    partner_id = fields.Many2one(comodel_name='res.partner',string='Partner Id')
    expired_date = fields.Datetime(
        string='Expired Date',
    ) 
    state =   fields.Selection(
        string='Status',
        selection= STATE_SELECTION,
    )

    def reload_data(self,kw):
        start_date = kw['start_date']
        end_date = kw['end_date']
        partner_id = kw['partner_id']

        res_partner = 'rp.name partner_name,' if partner_id else 'smr.partner_name partner_name,' 

        sql = """
            CREATE OR REPLACE VIEW  %s AS           
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            ap.name app_name,
            ap.price app_price,
            pp.name register_quantity,    
            smr.register_date date,
            smr.expired_date expired_date,
            smr.state state,
            %s
            rp.id partner_id

            FROM smart_manager_register smr 
            left join res_partner rp on smr.partner = rp.id
            left join smart_manager_register_app_price_rel pm on smr.id = pm.register_id
            left join smart_manager_app_price ap on pm.price_id = ap.id
            left join smart_manager_payment_period pp on ap.period = pp.id
                 
            WHERE 
            smr.register_date >= '%s 00:00:00' and smr.register_date <= '%s 23:59:59'
            AND smr.state IN('expired','activated')
        """%(self._table,res_partner,start_date,end_date)

        if partner_id:
            sql += """
            AND smr.partner = %s
            """%partner_id.id
        sql += """
        ORDER BY smr.register_date ASC
        """
        if 'vi_VN' in self._context.values():
                name = 'Báo cáo theo đối tác'
        else:
            name = 'Report partner'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.register.partner' ,
            "context":{'start_date':start_date, 'end_date':end_date}
                }
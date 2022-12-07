from odoo import fields,models,api,tools,_

class ReportRegisterOrder(models.Model):
    _name = 'report.register.order'
    _auto = False

    USING_TYPE_SELECTION = [('trial', _('Trial')), ('business',_('On Business'))]

    name_order = fields.Char(string='Name order')
    date = fields.Datetime(string='Date order')
    register_quantity = fields.Char(string='Register quantity')
    partner_id = fields.Many2one(comodel_name='res.partner')
    partner_name = fields.Char(string='Partner Name')
    amount_total = fields.Float(string='Total Amount')
    use_type =    fields.Selection(
        string='Using Type',
        selection=USING_TYPE_SELECTION
    )


    def reload_data(self,kw):
        start_date = kw['start_date']
        end_date = kw['end_date']
        partner_id = kw['partner_id']

        sql = """
            CREATE OR REPLACE VIEW  %s AS           
            SELECT 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id, 
            so.name name_order,
            so.date_order date,
            smpp.name register_quantity,
            rp.id partner_id,
            rp.name partner_name,
            so.amount_total amount_total,
            smr.use_type use_type


            FROM sale_order so
            LEFT JOIN sale_order_line sol on so.id = sol.id 
            LEFT JOIN res_partner rp on so.partner_id = rp.id
            LEFT JOIN smart_manager_register smr on so.order_register = smr.id
            LEFT JOIN smart_manager_payment_period smpp on smr.register_quantity = smpp.id
                 
            WHERE 
            so.date_order >= '%s 00:00:00' and so.date_order <= '%s 23:59:59'
        """%(self._table,start_date,end_date)

        if partner_id:
            sql += """
            AND so.partner = %s
            """%partner_id.id
        sql += """
        ORDER BY so.date_order ASC
        """
        if 'vi_VN' in self._context.values():
            name = 'Báo cáo hóa đơn'
        else:
            name = 'Report order'
        
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.register.order' ,
            "context":{'start_date':start_date, 'end_date':end_date}
                }
from odoo import api,models,fields,_,tools
import redis

class ReportTraffic(models.Model):
    _name = "report.traffic"
    _auto = False

    name_link = fields.Char(string='Name link')
    total_traffic = fields.Integer(string='Total traffic')

    def reload_data(self,kw):
        r = redis.StrictRedis(host="localhost",port=6379,password="",db=0)
        sql = """
        DELETE FROM temporary_report_traffic;
        CREATE OR REPLACE VIEW  %s AS
        SELECT 
        trp.id id,
        trp.name_link name_link,
        trp.total_traffic total_traffic
        FROM temporary_report_traffic trp
        """%self._table
        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        n=0
        for key in r.keys(kw['url']):
            
            data = r.hgetall(key.decode("utf8"))
            insert_values = """
                INSERT INTO %s (id,name_link,total_traffic)
                VALUES (%s,N'%s',%s)
            """ %(self._table,n,data[b'url'].decode("utf8"),int(data[b'count'].decode("utf8")))
            self.env.cr.execute(insert_values)
            n+=1

        if 'vi_VN' in self._context.values():
            name = 'Báo cáo theo khách hàng'
        else:
            name = 'Report customer'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "graph",
            "res_model": 'report.traffic' ,
            # "context":{'start_date':start_date, 'end_date':end_date}
                }



class TemporaryReportTraffic(models.Model):
    _name = 'temporary.report.traffic'
    
    name_link = fields.Char(string='Name link')
    total_traffic = fields.Integer(string='Total traffic')
            
from odoo import models, fields, api, tools
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import tempfile
from odoo.tools.misc import xlwt
import io
import base64
import time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import xlsxwriter

# import xlwt
# from xlsxwriter.workbook import Workbook
# from io import StringIO
# import io
# import base64

class ReportSaleGeneralGoods(models.Model):
    _name ='report.sale.general.goods'
    _auto = False
    _order = "product_name asc"
    id = fields.Integer(string='ID')
    product_code = fields.Char(string='Product code')
    product_name = fields.Char(string='Product name')
    unit = fields.Char(string='Unit')
    quantity = fields.Float(string='Quantity')
    gross_revenue = fields.Float(string='Gross revenue')
    discount = fields.Float(string='Discount')
    return_quantity = fields.Float(string='Return quantity')
    return_value = fields.Float(string='Value of return') 
    net_revenue = fields.Float('Net revenue')
    
    def reload_data(self,*kw):
        start_date =''
        end_date = ''
        product_list = kw[0].get('products',None)
        if len(kw)>0:
            start_date = kw[0].get('start_date')
            end_date = kw[0].get('end_date')
        else:    
            start_date =datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end_date =  datetime.today().strftime('%Y-%m-%d')
        prod_items = tuple(product_list.ids)
        if len(prod_items)<=1:
            prod_items = prod_items + tuple('0')+tuple('0')

        sql = """
             CREATE OR REPLACE VIEW %s AS
            select 
            ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS id,
            pt.default_code product_code,
            pt.NAME product_name,
            uu.NAME unit,
            sum(sol.product_uom_qty) quantity,
            sum(sol.product_uom_qty*sol.price_unit) gross_revenue,
            sum(sol.product_uom_qty*sol.price_unit*sol.discount/100) discount,
            0 return_quantity,
            0 return_value,
            sum(sol.price_subtotal) net_revenue

            from 
                sale_order_line sol 
                left join sale_order so on so.id = sol.order_id 
                left join product_product pp on pp.id = sol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join uom_uom uu on uu.id = pt.uom_id
                
                where so.state ='sale'
                and 
                so.date_order >= '%s 00:00:00'  AND so.date_order <= '%s 23:59:59'
                and pt.id in %s
                group by pt.default_code, pt.NAME,uu.NAME
                
                order by pt.name
        """ % ( self._table, start_date,end_date, prod_items)

        tools.drop_view_if_exists(self._cr, '%s' % self._table) 
        self.env.cr.execute(sql)
        if 'vi_VN' in self._context.values():
            name = 'Tổng hợp bán hàng theo hàng hóa'
        else:
            name = 'Report Sale by goods'

        return { 
            'name': name,
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": 'report.sale.general.goods' ,
            "context":{'start_date':start_date,'end_date':end_date}
                }

    @api.multi
    def generate_excel_report(self):
        filename= 'sale_goods_report' + '.xls'
        workbook= xlwt.Workbook()

        worksheet= workbook.add_sheet('Product Report')
        font = xlwt.Font()
        font.bold = True
        for_left = xlwt.easyxf("font: bold 1, color black; borders: top double, bottom double, left double, right double; align: horiz left")
        for_left_not_bold = xlwt.easyxf("font: color black; align: horiz left")
        for_center_bold = xlwt.easyxf("font: bold 1, color black; align: horiz center")
        GREEN_TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name Tahoma, height 250;'
            'align: vertical center, horizontal center, wrap on;'
            'borders: top double, bottom double, left double, right double;'
            )
        style = xlwt.easyxf('font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')

        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'

        worksheet.row(0).height = 320
        worksheet.col(0).width = 4000
        worksheet.col(1).width = 4000
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders

        product_title = 'Product Report '
        worksheet.write_merge(0,1,0,2,product_title,GREEN_TABLE_HEADER)
        
        row = 2

        worksheet.write(row, 0, 'Product Name' or '',for_left)
        worksheet.write(row, 1, 'Sales Price' or '',for_left)
        for rec in self:
            row = row + 1
            worksheet.write(row, 0, rec.product_name or '',for_left_not_bold)
            worksheet.write(row, 1, rec.product_code or '',for_left_not_bold)

        fp = io.BytesIO()
        workbook.save(fp)
        product_id = self.env['product.excel.extended'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return{
            'view_mode': 'form',
            'res_id': product_id.id,
            'res_model': 'product.excel.extended',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            # 'type' : 'ir.actions.act_url',
            # 'url': 'web/content/?model=product.excel.extended&field=excel_file&download=true&id=%s&filename=%s'%(product_id.id,filename),
            # 'target': 'new',
         }
    

class ProductExcelExtended(models.Model):
    _name = 'product.excel.extended'
    _description = "Product Excel Extended"


    # @api.one
    # def _get_template(self):
    #     r = open('sale_goods_report.xls', 'rb').read().encode('base64')
    #     self.excel_file = r

    excel_file = fields.Binary('Download Report :- ',attachment=True)
    file_name = fields.Char('Excel File', size=64)

    @api.multi
    def get_contract_template(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/product.excel.extended/5/excel_file/file_name?download=true',
        }
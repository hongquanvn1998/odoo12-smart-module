# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import werkzeug
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Date
import datetime
from odoo.http import Response
import requests
class SmartPos(http.Controller):
    # @http.route('/shop', auth="user")
    # def index(self, **kw):
    #     user = request.env.user
    #     pos_sessions = request.env['pos.session'].search([
    #         ('state', '=', 'opened'),
    #         ('seller_id', '=', request.session.uid),
    #         ('rescue', '=', False)])
    #     if not pos_sessions:
    #         return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
    #     # pos_sessions.login()
    #     pos_counter = http.request.env['pos.counter'].search([('id', '=', pos_sessions.config_id.id)])
    #     if not pos_counter:
    #         return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
    #     res_config_settings = http.request.env['res.config.settings'].sudo().get_values()
    #     if not res_config_settings:
    #         return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
    #     seller = http.request.env['res.users'].search([('id','=',request.session.uid)])
    #     if (seller is None):
    #         return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
    #     counter_config = {
    #         'counter_id': pos_counter.id,
    #         'session_id':pos_sessions.id,
    #         'counter_name': pos_counter.name,
    #         'counter_code': pos_counter.code,
    #         'company_id': pos_counter.company_id.id,
    #         'iot_gateway': pos_counter.iot_gateway,
    #         'barcode_scanner': pos_counter.barcode_scanner,
    #         'electronic_scale': pos_counter.electronic_scale,
    #         'cash_drawer': pos_counter.cash_drawer,
    #         'price_displayer' :pos_counter.price_displayer, 
    #         'pricelist_ids' :pos_counter.pricelist_ids.mapped('id'),
    #         'payment_method_ids' :pos_counter.payment_method_ids.mapped('id'), 
    #         'current_session_id' :pos_counter.current_session_id.id,
    #         'current_session_state' :pos_counter.current_session_state,
    #         '_picking_type' :pos_counter.stock_picking_type_id.id,
    #     }
    #     pos_seller = {
    #         'seller_id': seller.id,
    #         'seller_name': seller.partner_id.name
    #     }
    #     kw={'ids':pos_counter.payment_method_ids.mapped('id')}
    #     context = {
    #         'counter_config': counter_config,
    #         'config_settings': res_config_settings,
    #         'payment_method':  http.request.env['pos.payment.method'].sudo().get_list_payment(**kw),
    #         'seller':pos_seller
    #     }
    #     View = request.env['ir.ui.view'].sudo()
    #     content =    View.render_template('smart_pos.shop_layout',{'context':json.dumps(context)})
    #     return content
    

    @http.route('/shop', auth="user")
    def index(self,**kw):
        swift_code = kw.get('swift_code',False) 
        user = request.env.user
        pos_sessions = request.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('seller_id', '=', request.session.uid),
            ('uuid','=',swift_code),
            ('rescue', '=', False)])
        action = request.env.ref('smart_pos.pos_config_counter_action_dashboard').read()[0]   

        if not pos_sessions:
            return werkzeug.utils.redirect('/web#action=%s&model=pos.counter&view_type=kanban' % action['id'])

       

         
        view = request.env['ir.ui.view'].sudo()
        content =    view.render_template('smart_pos.shop_layout',{'context':{'url': '/web#action=%s&model=pos.counter&view_type=kanban' % action['id']}})
        return content
        

    @http.route('/api/load-session-config', auth='user', type='json', method=['POST'], csrf=False)
    def load_session_config(self,**kw):
        swift_code = kw.get('swift_code')
        uid = kw.get('uid')
        if not swift_code or not uid:
            return False

        pos_sessions = request.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('uuid','=',swift_code),
            ('seller_id', '=',  uid),
            ('rescue', '=', False)])
        if not pos_sessions:
            return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        # pos_sessions.login()
        # pos_counter = http.request.env['pos.counter'].search([('id', '=', pos_sessions.config_id.id)])
        # if not pos_counter:
        #     return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        res_config_settings = http.request.env['res.config.settings'].sudo().get_values()
        if not res_config_settings:
            return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        seller = http.request.env['res.users'].search([('id','=',request.session.uid)])
        if (seller is None):
            return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        counter_config = {
            'counter_id': pos_sessions.config_id.id,
            'session':[pos_sessions.id,pos_sessions.name,pos_sessions.openned],
            'counter_name': pos_sessions.config_id.name,
            'counter_code': pos_sessions.config_id.code,
            'company_id': pos_sessions.config_id.company_id.id,
            'iot_gateway': pos_sessions.config_id.iot_gateway,
            'barcode_scanner': pos_sessions.config_id.barcode_scanner,
            'electronic_scale': pos_sessions.config_id.electronic_scale,
            'cash_drawer': pos_sessions.config_id.cash_drawer,
            'price_displayer' :pos_sessions.config_id.price_displayer, 
            'pricelist_ids' :pos_sessions.config_id.pricelist_ids.mapped('id'),
            'payment_method_ids' :pos_sessions.config_id.payment_method_ids.mapped('id'), 
            'current_session_id' :pos_sessions.config_id.current_session_id.id,
            'current_session_state' :pos_sessions.config_id.current_session_state,
            '_picking_type' :pos_sessions.config_id.stock_picking_type_id.id,
            'company_name': pos_sessions.config_id.company_id.display_name,
            'company_address': (pos_sessions.config_id.company_id.tax_address if pos_sessions.config_id.company_id.tax_address != False else '%s %s %s'%(pos_sessions.config_id.company_id.street,pos_sessions.config_id.company_id.city,pos_sessions.config_id.company_id.state_id.name))
        }
        pos_seller = {
            'seller_id': seller.id,
            'seller_name': seller.partner_id.name
        }
        kw={'ids':pos_sessions.config_id.payment_method_ids.mapped('id')}
        context = {
            'counter_config': counter_config,
            'config_settings': res_config_settings,
            'payment_method':  http.request.env['pos.payment.method'].sudo().get_list_payment(**kw),
            'seller':pos_seller
        }
        
        return context
        
        


 

    # @http.route('/list',  type='http', auth='public', methods=['GET'])
    # def list(self, **kw):
    #     lst_product=[]
    #     http.request.env.cr.execute(
    #         """
    #         select pt.id,pt.name,pp.default_code,
    #         sq.quantity-sq.reserved_quantity inventory, sq.reserved_quantity purchase ,
    #         pt.list_price 
    #         from product_template  pt left join product_product pp on pp.product_tmpl_id =pt.id 
    #         left join stock_quant sq on pp.id= sq.product_id
    #         left join stock_location sl 
    #         on sl.id= sq.location_id
    #         where sq.quantity-sq.reserved_quantity >=0 
    #         """
    #     )
    #     # obj=http.request.env['product.category'].browse(2)
    #     # obj.write({'name':'update'})
    #     # http.request.env['product.category'].create({
    #     #     'name':'create',
    #     #     'complete_name':'create',
    #     #     'create_uid':1,
    #     # })
    #     # http.request.env['product.category'].search([('id','=','5')]).unlink()
       
    #     self.data= http.request.env.cr.fetchall()
    #     for item in self.data:
    #         vals={
    #             'id':item[0],
    #             'name':item[1],
    #             'code' :item[2],
    #             'quantity':1,
    #             'inventory':item[3],
    #             'purchase' :item[4],
    #             'price':item[5]

    #         }
    #         lst_product.append(vals)
    #     return json.dumps(lst_product)  
    
    #currenpayments: các phương thức thanh toán được add vào
        #Accountid: id của tải khoản ngân hàng
        #amout: số tiền thanh toán với phương thức đó
        #id: id của phương thức
        #method: code của phương thức
        #methodstr: string của phương thức
    #changeAmout: tiền thừa trả lại
    #customerPay: khách hàng trả
    #discount: giảm giá tính theo vnđ
    #discountPercent: giảm giá tính theo %
    #id: id của hóa đơn đó
    #idx: index của hóa đơn đó
    #items: các sản phẩm trong hóa đơn
        #baseprice: giá gốc
        #categoryid: id của danh mục sản phẩm
        #discountProd: giảm giá trên số tiền vnđ của sản phẩm
        #discountProdPercent: giảm giá trên % của sản phẩm
        #discountRatio: giảm giá trên % của sản phẩm (k cần quan tâm)
        #onhand: số lượng có trong kho
        #onhold: số lượng đang được reverse (giữ)
        #originPrice: giá gốc
        #productType: loại sản phẩm
        #quantity: số lượng đang được mua
        #saleprice: giá bản hiện tại
        #total: tổng tiền của sản phẩm
        #typediscount: kiểu giảm giá của sản phẩm (0 là vnđ hoặc 1 là %)
        #unit: đơn vị của sản phẩm
    #payingAmount: số tiền đang được trả trên hóa đơn
    #totalamount tổng tiền của hóa đơn
    #totalQuantity: tổng số sản phẩm được mua
    #typeDiscount: kiểu giảm giá của hóa đơn (giống sản phẩm)

    @http.route('/api/payment',csrf=False,type='json',auth='user',method=['POST'])
    def GetPosOrders(self, **kw):
        if (len(kw['pos_orders']['items']) <= 0 or int(kw['pos_orders']['totalQuantity']) <=0 or int(kw['pos_orders']['totalAmount']) <=0):
            data = {
                'message': 'Phiếu hàng đang trống!',
                'code': 400,
                'status' :False
            }
            return json.dumps(data)
        # try:
        flag_reward_point = False
        if 'currentCustomer' not in kw['pos_orders'] or kw['pos_orders']['currentCustomer'] is None:
            _customer_id = http.request.env['res.partner'].search([('customer_code','=','KH-00000000')])
            _customer_id = _customer_id.id
            flag_reward_point = True
        else:
            _customer_id=kw['pos_orders']['currentCustomer']['id']
        # except Exception:
        #      data = {
        #         'message': 'Khách hàng đang bỏ trống!',
        #         'code': 400,
        #         'status' :False
        #     }
        #      return json.dumps(data)     
                  
        _session_id = kw['counter_config']['session'][0]
        _company_id = kw['counter_config']['company_id']
        _counter_id = kw['counter_config']['counter_id']
        _changeAmount = kw['pos_orders']['changeAmount']
        if (_changeAmount < 0):
            data = {
                'message': 'Tiền thừa trả lại không được < 0!',
                'code': 400,
                'status' :False
            }
            return json.dumps(data)
        pos_sessions = request.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('id', '=',_session_id),
            ('seller_id', '=', request.session.uid),
            ('rescue', '=', False)])
        if not pos_sessions:
            return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        last_config = http.request.env['res.config.settings'].sudo().get_values()
        counter = http.request.env['pos.counter'].search([('id', '=', _counter_id)])
        if counter is None:
            data = {
                'message': 'Quầy thanh toán chưa tồn tại!',
                'code': 400,
                'status' :False
            }
            return json.dumps(data)            
        _payment_mothod = []
        _current_payment = kw['pos_orders']['CurrentPayments']
        _pos_order = kw['pos_orders']
        _points=0
        for payment in kw['pos_orders']['CurrentPayments']:
            _payment_mothod.append(payment['Id'])
            if (payment['Method'] == "Point" or payment['Method'] == "point" ):
                reward_point = http.request.env['pos.reward.point'].search([('partner_id', '=', _customer_id)])
                if(last_config['reward_point_is_point_to_money']==False and flag_reward_point == False):
                    data = {
                        'message': 'Quầy hàng hiện tại không cho thanh toán bằng điểm!',
                        'code': 400,
                        'status' :False
                    }
                    return json.dumps(data)
                if (last_config['allow_reward_invoice'] == True and last_config['reward_point_money_per_point'] <= 0 and flag_reward_point == False):
                    data = {
                        'message': 'Tỉ lệ quy đổi điểm thưởng chưa đúng. Số tiền quy đổi ra 1 điểm thưởng phải lớn hơn 0!.',
                        'code': 400,
                        'status' :False
                    }
                    return json.dumps(data)

                if(last_config['reward_point_is_point_to_money'] ==True and last_config['reward_point_point_to_money'] <=0 and last_config['reward_point_money_to_point'] <=0 and last_config['reward_point_invoice_count']<=0 and flag_reward_point == False):
                     data = {
                        'message': 'Cấu hình cho phép thanh toán bằng điểm chưa đúng!.',
                        'code': 400,
                        'status' :False
                     }
                     return json.dumps(data)                    
                if (reward_point.reward_count < last_config['reward_point_invoice_count'] and flag_reward_point == False):
                    data = {
                        'message': 'Bạn chỉ được thanh toán bằng điểm sau %s lần mua hàng!' %(last_config['reward_point_invoice_count']),
                        'code': 400,
                        'status' :False
                    }
                    return json.dumps(data)
                if (len(reward_point) <1   or reward_point.points < payment['point_used'] and flag_reward_point == False):
                    data = {
                        'message': 'Khách không đủ điểm để thanh toán .Khách chỉ có %s điểm!' %(reward_point.points),
                        'code': 400,
                        'status' :False
                    }
                    return json.dumps(data)
                else:
                    _points = payment['point_used']

        

        _stock_quant = http.request.env['stock.quant']
        _product_product = http.request.env['product.product']
        _picking_type = http.request.env['stock.picking.type'].search([('id', '=', int(counter.stock_picking_type_id))])
        _stock_location = http.request.env['stock.location'].search([('id', '=', int(_picking_type.default_location_src_id))])
        # _location_dest_id = http.request.env.ref('stock.stock_location_customers').id
        _location_dest_id = http.request.env['res.users'].search([('id', '=', request.session.uid)]).property_stock_customer.id
        if (_picking_type.warehouse_id.company_id != counter.company_id):
            data = {
                'message': 'Cấu hình công ty không đúng với kho/kiểu hoạt đông!.',
                'code': 400,
                'status' :False
                }
            return json.dumps(data)
        for item in kw['pos_orders']['items']:
            product = _product_product.search([('id', '=', int(item['id']))])
            quant = _stock_quant._get_available_quantity(product, _stock_location)
            if quant < int(item['quantity']):
                data = {
                'message': 'Sản phẩm %s không đủ số lượng trong %s. Hiện tại tồn kho %s!. ' %(product.product_tmpl_id.name,_picking_type.warehouse_id.name,quant),
                'code': 400,
                'status' :False
                }
                return json.dumps(data)

            if quant < 0:
                data = {
                'message': 'Sản phẩm %s chưa nhập số lượng' %(product.product_tmpl_id.name),
                'code': 400,
                'status' :False
                }
                return json.dumps(data)
            
            if (product.categ_id is None):
                    data = {
                    'message': 'Sản phẩm chưa có danh mục!.' ,
                    'code': 400,
                    'status' :False
                    }
                    return json.dumps(data)
            if (product.categ_id.property_stock_account_input_categ_id is None or product.categ_id.property_stock_account_output_categ_id is None or product.categ_id.property_stock_valuation_account_id is None):
                    data = {
                    'message': 'Bạn chưa nhập thuộc tính tài khoản kho!.' ,
                    'code': 400,
                    'status' :False
                    }
                    return json.dumps(data)
            if (product.categ_id.property_account_expense_categ_id is None or product.categ_id.property_account_income_categ_id is None):
                    data = {
                        'message': 'Bạn chưa nhập tài khoản kế toán!.' ,
                        'code': 400,
                        'status' :False
                        }
                    return json.dumps(data)
        _pricelist_id=[]
        for pricelist in kw['counter_config']['pricelist_ids']:
            _pricelist_id.append(pricelist)
        kw_pos_counter = kw['counter_config']
        kw = kw['pos_orders']
        default_code = http.request.env['pos.order'].sudo().default_order_code()

        payment_line_ids=[]
        if len(kw['CurrentPayments'] )> 0:
            for payment in kw['CurrentPayments']:
                try:
                    vars = {
                        'name':payment['MethodStr'] ,
                        'payment_method_id':payment['Id'],
                        'amount':payment['Amount'],
                        'session_id':_session_id,
                        'counter_id':_counter_id,
                        'seller_id':request.session.uid,
                        'partner_id':_customer_id,
                        # 'order_id':pos_order.id,
                        'journal_id':(payment['AccountId'] if payment['AccountId'] else http.request.env['pos.payment.method'].search([('id','=',payment['Id'])]).default_journal_id.id )
                        }
                    payment_line_ids.append((0,0,vars))
                    # http.request.env['pos.order.payment.line'].create(vars)
                except Exception as ex:
                    data = {
                    'message': 'Pos order payment line %s!' %(ex.args[0]),
                    'code': 400,
                    'status' :False
                     }
                    return json.dumps(data)
        else:
            try:
                vars = {
                    'name':http.request.env['pos.payment.method'].sudo()._get_cash().name ,
                    'payment_method_id':http.request.env['pos.payment.method'].sudo()._get_cash().id,
                    'amount':_pos_order['payingAmount'],
                    'session_id':_session_id,
                    'counter_id':_counter_id,
                    'seller_id':request.session.uid,
                    'partner_id':_customer_id,
                    # 'order_id':pos_order.id,
                    'journal_id':http.request.env['pos.payment.method'].sudo()._get_cash().default_journal_id.id 
                    }
                payment_line_ids.append((0,0,vars))
                # http.request.env['pos.order.payment.line'].create(vars)

            except Exception as ex:
                data = {
                'message': 'Pos order payment line %s!' %(ex.args[0]),
                'code': 400,
                'status' :False
                    }
                return json.dumps(data)

        pos_order_lines = []
        for item in kw['items']:
            product = _product_product.search([('id', '=', int(item['id']))])
            try:
                vars = {
                # 'name': '%s/%s/%s' %(counter.name,pos_order.code,pos_order.id),
                'note': '',
                'product_id': int(item['id']),
                'quantity':int( item['quantity']) or 0,
                'change_price': float(item['salePrice']) or 0,
                'price_unit':float(item['basePrice']) or 0,
                'discount': float(item['discountProdVND']) if item['discountProdVND'] and item['discountProdVND'] != None else 0,
                'discount_percent': float(item['discountProdPercent']) if item['discountProdPercent'] and item['discountProdPercent'] != None else 0,
                'price_subtotal': float(item['total']) or 0,
                # 'order_id':pos_order.id,
                }
                pos_order_lines.append((0,0,vars))
                # _pos_order_line_id = http.request.env['pos.order.line'].create(vars)
            except Exception as ex:
             data = {
                 'message': 'Pos order line %s!' %(ex.args[0]),
                 'code': 400,
                 'status' :False
             }
             return json.dumps(data)
            
        
        #Quân update 09/12/2020
        #Tạo pos.order, pos.order.line, pos.order.payment.line
        pos_order=http.request.env['pos.order'].create({
            'name': '%s-%s' %(counter.order_code,default_code),
            'code': 'DH-%s' %(default_code),
            'seller_id': request.session.uid,
            'partner_id': _customer_id,
            'company_id': _company_id,
            'date_order': datetime.datetime.now(),
            'qty_total': int(kw['totalQuantity']) or 0,
            'amount_total':float(kw['customerPay']) or 0,
            'discount': float(kw['discount']) if kw['discount'] or kw['discount']!= None else 0,
            'discount_percent': float(kw['discountPercent']) if kw['discountPercent'] or kw['discountPercent'] != None else 0,
            'amount_paid':float(kw['payingAmount']) or 0,
            'amount_return': float(kw['changeAmount']) or 0,
            'session_id': _session_id,
            'pricelist_ids': _pricelist_id,
            'payment_method_ids':_payment_mothod,
            'note':kw['description'] or None ,
            'counter_id':_counter_id,
            'payment_line_ids': payment_line_ids,
            'line_ids':pos_order_lines
        })

        stock_picking = http.request.env['stock.picking'].create({
                    'picking_type_id': counter.stock_picking_type_id.id,
                    'origin' :'%s/%s' %(pos_order.name,pos_order.id),
                    'location_id': _stock_location.id,
                    'location_dest_id': _location_dest_id,
                    'state': 'draft',
                    'partner_id': _customer_id,
                    'company_id': _company_id
                })
        stock_picking.action_confirm()

        try:
            for line_id in pos_order.line_ids:
                line_id.write({'name' : '%s/%s/%s' %(counter.name,pos_order.code,pos_order.id)})

                try:
                    stock_move_line = [(0, 0, {
                        'product_id':int(line_id.product_id.id) ,
                        'product_uom_id':int(line_id.product_id.uom_id.id),
                        'location_id': _stock_location.id,
                        'location_dest_id': _location_dest_id,
                        'picking_id': stock_picking.id,
                        'qty_done':int(line_id.quantity),

                    })]
                    stock_move = http.request.env['stock.move'].sudo().create({
                        'name': '%s' %(pos_order.name),
                        'product_id': int(line_id.product_id.id),
                        'picking_id': stock_picking.id,
                        'product_uom_qty': int(line_id.quantity),
                        'product_uom': int(line_id.product_id.uom_id.id),
                        'location_id': _stock_location.id,
                        'location_dest_id': _location_dest_id,
                        'picking_type_id': counter.stock_picking_type_id.id,
                        'order_line_id': line_id.id,
                        'move_line_ids': stock_move_line,
                        
                    })
                    stock_picking.action_done()
                    stock_move._action_assign()
                    stock_move.filtered(lambda m: m.product_id.tracking == 'none')._action_done()
                except Exception as ex:
                    data = {
                    'message': 'Stock %s!' %(ex.args[0]),
                    'code': 400,
                    'status' :False
                }
                    return json.dumps(data)
        except Exception as ex:
            pass

        

        #####################################################################

        reward_point = http.request.env['pos.reward.point'].search([('partner_id', '=', _customer_id)])
        if (reward_point.id == False and flag_reward_point == False or len(reward_point)<1 and flag_reward_point == False):
            # khách hàng cộng điểm  lần đầu
            if (last_config['allow_reward_invoice'] == True):
                if(int(_pos_order['customerPay']/last_config['reward_point_money_per_point'])>0):
                # cho phép tích điểm cho hóa đơn
                    reward = http.request.env['pos.reward.point'].create({
                        'partner_id': _customer_id,
                        'reward_count': 1,
                        'payment_count': 1,
                        'points': int(_pos_order['customerPay']/last_config['reward_point_money_per_point']),
                    })
                    reward_history = http.request.env['pos.reward.point.history'].create({
                        'counter_id': _counter_id,
                        'partner_id': _customer_id,
                        'order_id': pos_order.id,
                        'reward_point': int(_pos_order['customerPay'] / last_config['reward_point_money_per_point']),
                        'change_point':int(_pos_order['customerPay'] / last_config['reward_point_money_per_point']),
                    })
                else:
                    pass
            else:
                # Không cho phép tích điểm hóa đơn
                pass
        else :
            # update điểm cho khách hàng
            if (last_config['allow_reward_invoice'] == True and flag_reward_point == False):
                if (_points >0):
                    reward = reward_point.write({
                        'reward_count':reward_point['reward_count'] + 1,
                        'payment_count':reward_point['payment_count'] +1,
                        'points':(reward_point['points'] - _points + int(_pos_order['customerPay']/last_config['reward_point_money_per_point'])),
                    })
                    reward_history = http.request.env['pos.reward.point.history'].create({
                            'counter_id': _counter_id,
                            'partner_id': _customer_id,
                            'order_id': pos_order.id,
                            'payment_point':  _points,
                            'change_point': -_points,
                            'reward_point': int(_pos_order['customerPay'] / last_config['reward_point_money_per_point'])
                        })

                else:
                    reward = reward_point.write({
                        'reward_count':reward_point['reward_count'] +1,
                        'payment_count':reward_point['payment_count']+1,
                        'points':(reward_point['points'] - _points + int(_pos_order['customerPay']/last_config['reward_point_money_per_point'])),
                    })
                    reward_history = http.request.env['pos.reward.point.history'].create({
                            'counter_id': _counter_id,
                            'partner_id': _customer_id,
                            'order_id': pos_order.id,
                            'reward_point': int(_pos_order['customerPay'] / last_config['reward_point_money_per_point'])+ _points,
                            'change_point':int(_pos_order['customerPay'] / last_config['reward_point_money_per_point']) + _points,
                        })
            else:
                pass        
        _order = ([{
                'partner_name': order.partner_id.name,
                'company_name': counter.company_id.name,
                'company_address':'%s-%s-%s-%s'  %(counter.company_id.province.name or '',counter.company_id.district.name or '',counter.company_id.ward.name or '',counter.company_id.street_address or ''),
                'counter_name': counter.name ,
                'mobile': order.partner_id.mobile or '',
                'address':'%s %s %s %s'  %(order.partner_id.province.name or '',order.partner_id.district.name or '', order.partner_id.ward.name or '', order.partner_id.street_address or ''),
                'order_name': order.name,
                'seller_name': order.seller_id.name,
                'amount_total': order.amount_total + order.discount,
                'customer_pay':order.amount_total,
                'discount': order.discount,
                'amount_return': order.amount_return,
                'amount_paid' :order.amount_paid,
                'date_order':order.date_order.strftime('%d/%m/%Y'),
                'lines': [
                    {
                     'product_name':item.product_id.name,
                     'price_unit':item.price_unit,
                     'qty': item.quantity,
                     'sub_total': item.price_subtotal,
                     'discount':item.discount,
                     'barcode': item.product_id.barcode or '',
                     'change_price' : item.change_price,
                } for item in order.line_ids]
        } for order in pos_order])
        
        if len(kw['tracebility_code']) > 0:
            tracebility_code = []
            for key in kw['tracebility_code'].keys():
                tracebility_code.append(key)
            tracebility_code_str = ','.join(tracebility_code)
            company_address = http.request.env['res.partner'].search([('id','=',kw_pos_counter['company_id'])])
            company_street = '%s, ' %(company_address.street_address) if company_address.street_address else ''
            company_ward = '%s, ' %(company_address.ward.name) if company_address.ward else ''
            company_district = '%s, ' %(company_address.district.name) if company_address.district else ''
            company_province = '%s, ' %(company_address.province.name) if company_address.province else ''
            _company_address = company_street + company_ward + company_district + company_province
            if '_customer_id' in locals():
                address_street = '%s, ' %(_customer_id.street_address) if _customer_id.street_address else ''
                address_ward = '%s, ' %(_customer_id.ward.name) if _customer_id.ward else ''
                address_district = '%s, ' %(_customer_id.district.name) if _customer_id.district else ''
                address_province = '%s ' %(_customer_id.province.name) if _customer_id.province else ''
            else:
                address_street = '%s, ' %(kw['currentCustomer']['street_address']) if len(kw['currentCustomer']['street_address']) >0 else ''
                address_ward = '%s, ' %(kw['currentCustomer']['ward_name']) if len(kw['currentCustomer']['ward_name']) >0 else ''
                address_district = '%s, ' %(kw['currentCustomer']['district_name']) if len(kw['currentCustomer']['district_name']) >0 else ''
                address_province = '%s ' %(kw['currentCustomer']['province_name']) if len(kw['currentCustomer']['province_name']) >0  else ''
            _customer_address = address_street + address_ward + address_district + address_province
            
            all_sell = {
                "stamp_code": tracebility_code_str,
                "stamp_serial": "",
                "seller_name": company_address.name,
                "seller_address": _company_address,
                "buyer_name": (kw['currentCustomer']['name'] if 'currentCustomer' in kw else _customer_address.name),
                "buyer_address": _customer_address,
                "buyer_phone": (kw['currentCustomer']['mobile'] if 'currentCustomer' in kw else _customer_address.mobile),
                "buyer_email": (kw['currentCustomer']['email'] if 'currentCustomer' in kw else _customer_address.email)
            }
            response = requests.post("http://api.smartlifevn.com/23hdy653ja9862hj/pos/sell",json=all_sell)
            data_response = response.json()
        data = {
                'message': 'Thanh toán thành công!',
                'message_tracebility': (data_response['message'] if 'data_response' in locals() else '') ,
                'code': 200,
                'status': True,
                'result':_order
            }
        return json.dumps(data)
    
    @http.route('/api/bank-account',csrf=False,type='http',auth='user',method=['POST'])
    def BankAccount(self,**kw):
        lst_bank = []
        http.request.env.cr.execute(
            """
                select aj.id, aj.name, aj.bank_account_id,
                rpb.acc_number,
                rb.name
                from account_journal aj left join res_partner_bank rpb on aj.bank_account_id = rpb.id
                left join res_bank rb on rpb.bank_id = rb.id
                where aj.type = 'bank'
            """
        )
        self.data = http.request.env.cr.fetchall()
        for item in self.data:
            vals = {
                "id": item[0],
                "name": item[1],
                "bank_account_id": item[2],
                'acc_number':item[3],
                'name_bank':item[4],
            }
            lst_bank.append(vals)
        return json.dumps(lst_bank)

    @http.route('/api/area',csrf=False,type="http",auth="user",method=['POST'])
    def getArea(self,**kw):
        response_province = http.request.env['province'].search([])
        list_province=[]
        list_district=[]
        list_ward = []
        if len(kw)<1:
            for res in response_province:
                val = {
                    'id': res.id,
                    'name': res.name,
                    'code_province':res.code_province,
                    'is_province':True,
                }
                list_province.append(val)
        elif 'province_id' in kw:
            for t in http.request.env['district'].search([('parent_code','=',kw['province_id'])]):
                val_t = {
                    'id': t.id,
                    'name': t.name,
                    'parent_code':t.parent_code,
                    'code_district':t.code_district,
                    'is_district':True,
                }
                list_district.append(val_t)
        else:
            for w in http.request.env['ward'].search([('parent_code','=',kw['district_id'])]):
                val_w = {
                    'id': w.id,
                    'name': w.name,
                    'parent_code':w.parent_code,
                    'is_ward':True,
                }
                list_ward.append(val_w)
        data = {
            'province':list_province,
            'district':list_district,
            'ward':list_ward,
        }
        return json.dumps(data)
        
    @http.route('/api/customer',csrf=False,type="http",auth="user",method=['POST'])
    def customer(self,**kw):
        # try:
        response = request.env['res.partner'].sudo()
        http.request.env.cr.execute(
            """
                select rp.id,rp.name,rp.vat,rp.customer_code,rp.mobile,rp.title,rp.facebook,rp.comment,rp.is_company,rp.email,
                prp.id,prp.partner_id,prp.points,prp.reward_count,prp.payment_count,rp.birthday,rp.street_address,rp.province,rp.district,rp.ward,rp.create_uid
                from res_partner rp left join pos_reward_point prp on prp.partner_id = rp.id
                where rp.active = true
                and rp.customer = true
                and rp.customer_code != 'KH-00000000'
            """
        )
        # list_customer = response.search([])
        list_customer = http.request.env.cr.fetchall()
        list_add = []
        data = {}
        if len(kw) > 0:
            kw['birthday'] = datetime.datetime.strptime(kw['birthday'],'%d/%m/%Y') if 'birthday' in kw and len(kw['birthday']) > 0 else None
            if not list_customer or list_customer and len(list_customer)<1:
                response.create(kw)
            else:
                loop = False
                for i in list_customer:
                    if 'id' in kw and i[0] == int(kw['id']):
                        response.search([('id','=',kw['id'])]).write(kw)
                        loop = True
                        data['message'] = 'Cập nhật khách hàng thành công'
                if loop == False:
                    response.create(kw)
                    data['message'] = 'Tạo khách hàng thành công'
        for e in list_customer:
            province = http.request.env['province'].search([('id','=',e[17])])
            district = http.request.env['district'].search([('id','=',e[18])])
            ward = http.request.env['ward'].search([('id','=',e[19])])
            image = http.request.env['res.partner'].search([('id','=',e[0])])

            vals = {
                'id':e[0],
                'name': e[1],
                'vat': (e[2] if e[2] else ''),
                'customer_code':(e[3] if e[3] else ''),
                'mobile':(e[4] if e[4] else ''),
                'title':(str(e[5]) if e[5] else ''),
                'facebook':(e[6] if e[6] else ''),
                'comment':(e[7] if e[7] else ''),
                'company_type':('company' if e[8] else 'person'),
                'email':(e[9] if e[9] else ''),
                'birthday':(e[15].strftime("%m/%d/%Y") if e[15] else ''),
                'street_address':(e[16] if e[16] else ''),
                'province':province.id or '',
                'district':district.id or '',
                'ward':ward.id or '',
                'province_name':province.name or '',
                'district_name':district.name or '',
                'ward_name':ward.name or '',
                'creater_customer':http.request.env['res.users'].search([('id','=',e[20])]).partner_id.name,
                'prp_id':(e[10] if e[10] else None),
                'prp_partner_id':(e[11] if e[11] else None),
                'prp_points':(e[12] if e[12] else 0),
                'prp_reward_count':(e[13] if e[13] else 0),
                'prp_payment_count':(e[14] if e[14] else 0),
            }
            list_add.append(vals)
        data['customer'] = list_add
        json_response = json.dumps(data)
        return json_response

    @http.route('/api/product',csrf=False,type='http',auth='user',method=['POST'])
    def PosProduct(self,**kw): 
        location_id = http.request.env['stock.picking.type'].search([('id','=',kw["_picking_type"])]).default_location_src_id.id
        return json.dumps([{
                'id':_prod['id'],
                'name':_prod['display_name'],
                'defaultCode' :(_prod['default_code'] if _prod['default_code'] else ''),
                'onHand': http.request.env['stock.quant'].search([('product_id','=',_prod['id']),('location_id','=',location_id)]).quantity or 0,# _prod['qty_available']
                'onHold':_prod['outgoing_qty'], 
                'basePrice':_prod['list_price'],
                'salePrice':_prod['list_price'],
                'cost':_prod['standard_price'],
                'productType':_prod['type'],
                'unit':_prod['uom_name'],
                'unitId':_prod['uom_id'].id,
                'product_uom_id':_prod['uom_po_id'].id,
                'catetgoryId':_prod['categ_id'].id,
                'discountProd':0,
                'discountProdVND':0,
                'discountProdPercent':0,
                'discountRatio':None,
                'typeDiscount':0,
                'barcode':_prod['barcode'],
                'traceability_id':_prod['traceability_id'],
                # 'quantity':1,
                'image':'/web/image?model=product.template&id=%d&field=image' %_prod['id'],
                'attrvalues': _prod['attribute_line_ids'].ids,
        }  for _prod in request.env['product.product'].search([('pos_enable','=',True)])])


    # ThiepWong added: Day la cach goi chuan cho ham POST, va dau vao, dau ra chuan cua odoo. Sau se su dung phuong an nay!
    @http.route('/api/area-fetched',csrf=False,type="json",auth="user",method=['POST'])
    def pos_area(self,**kw):
        response_province = http.request.env['province'].search([])
        list_province=[]
        list_district=[]
        list_ward = []
        if len(kw)<1:
            for res in response_province:
                val = {
                    'id': res.id,
                    'name': res.name,
                    'province_code':res.code_province,
                    'is_province':True,
                }
                list_province.append(val)
        elif 'province_code' in kw:
            for t in http.request.env['district'].search([('parent_code','=',kw['province_code'])]):
                val_t = {
                    'id': t.id,
                    'name': t.name,
                    'parent_code':t.parent_code,
                    'district_code':t.code_district,
                    'is_district':True,
                }
                list_district.append(val_t)
        elif 'district_code' in kw:
            for w in http.request.env['ward'].search([('parent_code','=',kw['district_code'])]):
                val_w = {
                    'id': w.id,
                    'name': w.name,
                    'parent_code':w.parent_code,
                    'is_ward':True,
                }
                list_ward.append(val_w)
        data = {
            'province':list_province,
            'district':list_district,
            'ward':list_ward,
        }
        return  data 
         
    # ThiepWong added: Day la cach goi chuan cho ham POST, va dau vao, dau ra chuan cua odoo. Sau se su dung phuong an nay!
    @http.route('/api/product-list',csrf=False,type='json',auth='user',method=['POST'])
    def pos_product(self,**kw): 
        location_id = http.request.env['stock.picking.type'].search([('id','=',kw["picking_type"])]).default_location_src_id.id
        return  [{
                'id':_prod['id'],
                'name':_prod['name'],
                'defaultCode' :(_prod['default_code'] if _prod['default_code'] else ''),
                'onHand': http.request.env['stock.quant'].search([('product_id','=',_prod['id']),('location_id','=',location_id)]).quantity or 0,# _prod['qty_available']
                'onHold':_prod['outgoing_qty'], 
                'basePrice':_prod['list_price'],
                'salePrice':_prod['list_price'],
                'cost':_prod['standard_price'],
                'productType':_prod['type'],
                'unit':_prod['uom_name'],
                'unitId':_prod['uom_id'].id,
                'product_uom_id':_prod['uom_po_id'].id,
                'catetgoryId':_prod['categ_id'].id,
                'discountProd':0,
                'discountProdVND':0,
                'discountProdPercent':0,
                'discountRatio':None,
                'typeDiscount':0,
                'barcode':_prod['barcode'],
                'traceability_id':_prod['traceability_id'],
                # 'quantity':1,
                'image':'/web/image?model=product.template&id=%d&field=image' %_prod['id'],
                'attrvalues': _prod['attribute_line_ids'].ids,
        }  for _prod in request.env['product.product'].search([('pos_enable','=',True)])]
        
    # ThiepWong added: Day la cach goi chuan cho ham POST, va dau vao, dau ra chuan cua odoo. Sau se su dung phuong an nay!
    @http.route('/api/customer-list',csrf=False,type="json",auth="user",method=['POST'])
    def pos_customer(self,**kw):
        # try:
        response = request.env['res.partner'].sudo()
        http.request.env.cr.execute(
            """
                select rp.id,rp.name,rp.vat,rp.customer_code,rp.mobile,rp.title,rp.facebook,rp.comment,rp.is_company,rp.email,
                prp.id,prp.partner_id,prp.points,prp.reward_count,prp.payment_count,rp.birthday,rp.street_address,rp.province,rp.district,rp.ward,rp.create_uid
                from res_partner rp left join pos_reward_point prp on prp.partner_id = rp.id
                where rp.active = true
                and rp.customer = true
            """
            
                # and rp.customer_code != 'KH-00000000'
        ) 
        list_customer = http.request.env.cr.fetchall()
        customers = []
        data = {}
        try:
            
            if len(kw) > 0:
                kw['birthday'] = datetime.datetime.strptime(kw['birthday'],'%d/%m/%Y') if 'birthday' in kw and len(kw['birthday']) > 0 else None
                if not list_customer or list_customer and len(list_customer)<1:
                    response.create(kw)
                else:
                    loop = False
                    for i in list_customer:
                        if 'id' in kw and i[0] == int(kw['id']):
                            response.search([('id','=',kw['id'])]).write(kw)
                            loop = True
                            data['code'] = 200
                            data['message'] = 'Cập nhật khách hàng thành công'
                    if loop == False:
                        response.create(kw)
                        data['code'] = 200
                        data['message'] = 'Tạo khách hàng thành công'
            for e in list_customer:
                province = http.request.env['province'].search([('id','=',e[17])])
                district = http.request.env['district'].search([('id','=',e[18])])
                ward = http.request.env['ward'].search([('id','=',e[19])])
                image = http.request.env['res.partner'].search([('id','=',e[0])])
                vals = {
                    'id':e[0],
                    'name': e[1],
                    'tax_code':  e[2] or False,
                    'customer_code':  e[3] or False ,
                    'mobile':  e[4] or False  ,
                    'title':e[5] or False ,
                    'facebook':   e[6] or False,
                    'comment': e[7]  or False,
                    'company_type':('company' if e[8] else 'person'),
                    'email': e[9] or False ,
                    'birthday':(e[15].strftime("%m/%d/%Y") if e[15] else False),
                    'street_address': e[16] or False ,
                    'province': (province.id  ,province.name   ) if province else (),
                    'district':(district.id,district.name) if district else (),
                    'ward':  (ward.id,ward.name ) if ward else (),   
                    'create_by':http.request.env['res.users'].search([('id','=',e[20])]).partner_id.name,
                    'pos_reward_id': e[10] or False,
                    'pos_reward_partner_id': e[11] or False,
                    'pos_reward_points':e[12] or 0,
                    'pos_reward_reward_count':e[13] or 0,
                    'pos_reward_payment_count':   e[14] or 0,
                }
                customers.append(vals)
            data['customers'] = customers
        except Exception as e:
            data['code'] = 400
            data['message'] = e
        return data

    @http.route('/api/start-session', type="json", auth="user", method =['POST'])
    def start_session(self, **kw):
        user = request.env.user
        pos_sessions = request.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('seller_id', '=', request.session.uid),
            ('rescue', '=', False)])
        
        if not pos_sessions:
            return 'Have no POS session'
        pos_counter = http.request.env['pos.counter'].search([('id', '=', pos_sessions.config_id.id)])
        if not pos_counter:
            return 'Have no POS counter'
        res_config_settings = http.request.env['res.config.settings'].sudo().get_values()
        if not res_config_settings:
            return 'Have no POS counter settings'
        seller = http.request.env['res.users'].search([('id','=',request.session.uid)])
        if (seller is None):
            return 'Have no seller activated'
        

        # if not pos_sessions:
        #     return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        # # pos_sessions.login()
        # pos_counter = http.request.env['pos.counter'].search([('id', '=', pos_sessions.config_id.id)])
        # if not pos_counter:
        #     return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        # res_config_settings = http.request.env['res.config.settings'].sudo().get_values()
        # if not res_config_settings:
        #     return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')
        # seller = http.request.env['res.users'].search([('id','=',request.session.uid)])
        # if (seller is None):
        #     return werkzeug.utils.redirect('/web#action=smart_pos.action_client_smart_pos_menu')

        counter_config = {
            'counter_id': pos_counter.id,
            'session':[pos_sessions.id,pos_sessions.name,pos_sessions.openned],
            'counter_name': pos_counter.name,
            'counter_code': pos_counter.code,
            'company_id': pos_counter.company_id.id,
            'iot_gateway': pos_counter.iot_gateway,
            'barcode_scanner': pos_counter.barcode_scanner,
            'electronic_scale': pos_counter.electronic_scale,
            'cash_drawer': pos_counter.cash_drawer,
            'price_displayer' :pos_counter.price_displayer, 
            'pricelist_ids' :  [( price_list['id'], price_list['name']) for price_list in pos_counter.pricelist_ids],
            'payment_method_ids' : [ (method['id'], method['name'])  for method in pos_counter.payment_method_ids], 
            'current_session_id' :pos_counter.current_session_id.id,
            'current_session_state' :pos_counter.current_session_state,
            '_picking_type' :pos_counter.stock_picking_type_id.id,

        }
        pos_seller = {
            'seller_id': seller.id,
            'seller_name': seller.partner_id.name
        }
        kw={'ids':pos_counter.payment_method_ids.mapped('id')}
        context = {
            'counter_config': counter_config,
            'config_settings': res_config_settings,
            'payment_method':  http.request.env['pos.payment.method'].sudo().get_list_payment(**kw),
            'seller':pos_seller
        }
    
        return context
        
    # ThiepWong added: Day la cach goi chuan cho ham POST, va dau vao, dau ra chuan cua odoo. Sau se su dung phuong an nay!
    @http.route('/api/bank-account-list',csrf=False,type='json',auth='user',method=['POST'])
    def pos_bank_accounts(self,**kw):
        lst_bank = []
        http.request.env.cr.execute(
            """
                select aj.id, aj.name, aj.bank_account_id,
                rpb.acc_number,
                rb.name
                from account_journal aj left join res_partner_bank rpb on aj.bank_account_id = rpb.id
                left join res_bank rb on rpb.bank_id = rb.id
                where aj.type = 'bank'
            """
        )
        self.data = http.request.env.cr.fetchall()
        for item in self.data:
            vals = {
                "id": item[0],
                "name": item[1],
                "bank_account_id": item[2],
                'acc_number':item[3],
                'name_bank':item[4],
            }
            lst_bank.append(vals)
        return lst_bank 


    @http.route('/api/category-product',csrf=False,type='http',auth='user',method=['POST'])
    def CategoryProduct(self,**kw):
        lst_category = []
        lst_ex =[]
        http.request.env.cr.execute(
            """
                select pc.id, pc.name, pc.parent_id,pc.parent_path
                from product_category pc
            """
        )
        self.data = http.request.env.cr.fetchall()
        for item in self.data:
            vals = {
                "id": item[0],
                "name": item[1],
                "parentId": item[2],
                "hasChildren": False,
                'checked':False,
            }
            if item[2] and len(lst_category) > 0:
                for i in lst_category:
                    if item[2] == i['id']:
                        i['hasChildren'] = True
            lst_category.append(vals)
        if len(kw) > 0:
            for lst in lst_category:
                if lst['parentId'] == int(kw['id']):
                    lst_ex.append(lst)
                else:
                    continue
        my_list = [lst_ex,lst_category]
        return json.dumps(my_list)
    
    @http.route('/api/product-attribute',csrf=False,type='http',auth='user',method=['POST'])
    def ProductAttribute(self,**kw):
        lst_attr = []
        lst_attribute = request.env['product.attribute'].search([])
        for i in lst_attribute:
            values_id = request.env['product.attribute.value'].search([('attribute_id','=',i.id)])
            vals = {
                'id':i.id,
                'name':i.name,
                'values':[],
            }
            for value in values_id:
                push_value = {
                    'id':value.id,
                    'name':value.name,
                    'attribute_id':value.attribute_id.id,
                    'checked':False,
                }
                vals['values'].append(push_value)
            lst_attr.append(vals)
        return json.dumps(lst_attr)
    
    @http.route('/api/get-product-tracebility-by-code',csrf=False,type='http',auth='user',method=['POST'])
    def GetInfoTracebility(self,**kw):
        response = requests.get("http://api.smartlifevn.com/23hdy653ja9862hj/pos/getinfo",params={'code':kw['code']})
        data_response = response.json()
        if data_response['status'] == True:
            data = {
                'message': 'Tồn tại',
                'code': 200,
                'status': True,
                'data':data_response['data']
            }
            return json.dumps(data)
        else:
            data = {
                'message': data_response['message'],
                'code': 400,
                'status': False,
            }
            return json.dumps(data)
    
    @http.route('/api/get-product-by-barcode',csrf=False,type='http',auth='user',method=['POST'])
    def GetInfoBarcode(self,**kw):
        response = requests.get("http://mobile-api.nbc.gov.vn:9002/api/product?gtin=%s"%kw['code'])
        data_response = response.json()
        if data_response['success'] == 1:
            body = data_response['body']
            if body['item']['gtin'] != None:
                data = {
                    'message': 'Tồn tại',
                    'code': 200,
                    'status': True,
                    'data':body['item']
                }
            else:
                data = {
                    'message': 'Sản phẩm không được đăng ký',
                    'code': 400,
                    'status': False,
                }
        elif data_response['error'] != None :
            data = {
                    'message': 'Sản phẩm không được đăng ký',
                    'code': 400,
                    'status': False,
                }
        return json.dumps(data)

    @http.route('/api/check-session', type="json", auth="user", method =['POST'])
    def check_session(self, **kw):
        pos_sessions = request.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('id', '=',kw['_session_id']),
            ('seller_id', '=', request.session.uid),
            ('rescue', '=', False)])
        data = {
            'openned': False if not pos_sessions else True,
            }
        return data

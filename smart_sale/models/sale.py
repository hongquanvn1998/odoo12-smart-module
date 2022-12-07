from odoo import models, fields,api



class SaleOrder(models.Model):
      _inherit = 'sale.order'

      customer_address = fields.Char(string='Customer Address',default=None )
      customer_tax_code=  fields.Char(string='Customer Tax Code',default=None)
      consignee = fields.Char(string='Consignee')
      read_number=fields.Char(string='Read Number',compute="reader_number",store=False)

      is_completed = fields.Boolean(string="Is completed", compute='compute_is_completed',store=False)
      is_blue = fields.Boolean(string="Is blue", compute='compute_is_completed',store=False)

      picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=False,
        readonly=False,
        states={'draft': [('readonly', False)]})

      # picking_type_id = fields.Many2one(
      #   'stock.picking.type', 'Operation Type',
      #   required=True,
      #   readonly=True,
      #   states={'draft': [('readonly', False)]})

      @api.depends('picking_ids', 'picking_ids.state')
      def compute_is_completed(self):
            for order in self:
                  if order.picking_ids and all([x.state in ['done', 'cancel'] for x in order.picking_ids]):
                        order.is_completed = True
                  for od in order.order_line:
                        if od.qty_delivered > 0:
                              order.is_blue = True
                              break
                        else:
                              order.is_blue = False
                              continue

      @api.onchange('partner_id')
      def _get_partner_info(self):
            result  =''
            if self.partner_id is False:
                  pass
            else :
                  if self.partner_id.street is False : result  ==''
                  else :
                        result += str(self.partner_id.street) + str('-')
                  if self.partner_id.city is False : result  == result 
                  else :
                        result  +=  str('-') +  str(self.partner_id.city)
                  if self.partner_id.state_id.name is False :result == result 
                  else :
                        result  += str('-')  + str(self.partner_id.state_id.name)
            self.customer_tax_code = self.partner_id.vat
            self.customer_address=  result
      
      @api.multi
      @api.depends("amount_total")
      def reader_number(self):
            number_read = ('không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười')
            muoi = 'mươi'
            tram = 'trăm'
            nghin = 'nghìn'
            trieu = 'triệu'
            ty = 'tỷ'
            mot = 'mốt'
            tu = 'tư'
            lam = 'lăm'
            linh = 'linh'
            read_num_null = True
            s = int(self.amount_total)
            
            def _int(c):
                  return ord(c) - ord('0') if c else 0
            def _LT1e2(s):
                  if len(s) <= 1: return number_read[_int(s)]
                  if s[0] == '1':
                        ret = number_read[10]
                  else:
                        ret = number_read[_int(s[0])]
                        if muoi: ret += ' ' + muoi
                        elif s[1] == '0': ret += ' mươi'
                  if s[1] != '0':
                        ret += ' '
                        if   s[1] == '1' and s[0] != '1': ret += mot
                        elif s[1] == '4' and s[0] != '1': ret += tu
                        elif s[1] == '5': ret += lam
                        else: ret += number_read[_int(s[1])]
                  return ret
            def _LT1e3( s):
                  if len(s) <= 2: return _LT1e2(s)
                  if s == '000': return ''
                  ret = number_read[_int(s[0])] + ' ' + tram
                  if s[1] != '0':
                        ret += ' ' + _LT1e2(s[1:])
                  elif s[2] != '0':
                        ret += ' ' + linh + ' ' + number_read[_int(s[2])]
                  return ret
            def _LT1e9( s):
                  if len(s) <= 3: return _LT1e3(s)
                  if s == '000000' or s == '000000000': return ''
                  mid = len(s) % 3 if len(s) % 3 else 3
                  left, right = _LT1e3(s[:mid]), _LT1e9(s[mid:])
                  hang = nghin if len(s) <= 6 else trieu
                  if not left:
                        if not read_num_null: return right
                        else: return number_read[0] + ' ' + hang + ' ' + right
                  if not right: return left + ' ' + hang
                  return left + ' ' + hang + ' ' + right 
            def _arbitrary( s):
                  if len(s) <= 9: return _LT1e9(s)
                  mid = len(s) % 9 if len(s) % 9 else 9
                  left, right = _LT1e9(s[:mid]), _arbitrary(s[mid:])
                  hang = ' '.join([ty] * ((len(s) - mid) // 9))
                  if not left:
                        if not read_num_null: return right
                        elif right: return number_read[0] + ' ' + hang + ' ' + right
                        else: return right
                  if not right: return left + ' ' + hang
                  return left + ' ' + hang + ' ' + right 
            
            self.read_number = _arbitrary(str(s).lstrip('0')).title() + ' đồng'
      
      @api.multi
      def action_view_delivery_push(self):
            action = self.env.ref('stock.action_picking_tree_all').read()[0]

            pickings = self.mapped('picking_ids')
            if len(pickings) > 1:
                  action['domain'] = [('id', 'in', pickings.ids)]
            elif pickings:
                  action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
                  action['res_id'] = pickings.id
            return action

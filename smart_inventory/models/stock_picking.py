from odoo import models, fields, api,_
from odoo.exceptions import UserError
from lxml import etree
from odoo.osv.orm import setup_modifiers

class Picking(models.Model):
    _inherit = 'stock.picking'

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        readonly=True, required=True,
        states={'draft': [('readonly', False)],'assigned':[('readonly',False)]})
    
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        readonly=False, required=True,
        states={'draft': [('readonly', False)],'assigned':[('readonly',False)]})

    purchase_invoice_number = fields.Char(string="Purchase Invoice" ) 
    purchase_invoice_date = fields.Date(string="Invoice Date")
    warehouse = fields.Char(string="Warehouse", compute= "_warehouse_compute", store=True)
    debit = fields.Char(string="Debit")
    credit = fields.Char(string="Credit")

    # is_purchase = fields.Boolean(string="Is purchase", compute='compute_is_sale_purchase',store=True)
    # is_sale = fields.Boolean(string="Is sale", compute='compute_is_sale_purchase',store=True)
    # cost = fields.Float(string="Cost")
    # amount = fields.Float(string="Amount")

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True, readonly=False) 

    # @api.model
    # def _fields_view_get(self, arch):
    #     arch = super(Picking, self)._fields_view_get(arch)
    #     # render the partner address accordingly to address_view_id
    #     doc = etree.fromstring(arch)
    #     if doc.xpath("//field[@name='picking_type_id']"):
    #         return arch
    #     for node in doc.xpath("//field[@name='picking_type_id']"):
    #         node.set('invisible', '1')
    #         node.set('required', '1')
    #     arch = etree.tostring(doc, encoding='unicode')
    #     return arch
    
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Picking, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if self._context:
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//field[@name='picking_type_id']"):
    #             node.set('invisible', '1')
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res

    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        """
            Add domain 'allow_check_writting = True' on journal_id field and remove 'widget = selection' on the same
            field because the dynamic domain is not allowed on such widget
        """
        res = super(Picking, self).fields_view_get( view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='picking_type_id']")
        if doc is not None :
            for node in nodes:
                node.set('invisible', '1')
            res['arch'] = etree.tostring(doc)
        return res

    # @api.multi
    # @api.depends('sale_id', 'purchase_id')
    # def compute_is_sale_purchase(self):
    #     for order in self:
    #         if order.sale_id:
    #             order.is_sale = True
    #         elif order.purchase_id:
    #             order.is_purchase = True
    #         else:
    #             order.is_sale = False
    #             order.is_purchase = False
    # @api.onchange('is_purchase','is_sale')
    # def change_product(self):
    #     if self.is_sale == True:
    #         domain1 = self.env['stock.picking.type'].search([('code','=','outgoing')]).id
    #     elif self.is_purchase == True:
    #         domain1 = self.env['stock.picking.type'].search([('code','=','incoming')]).id
    #     else:
    #         domain1 = self.env['stock.picking.type'].search([('code','=','internal')]).id
    #     return {'domain': {'picking_type_id': [('id', '=',domain1)]}}

    @api.model
    @api.depends('picking_type_id')
    def _warehouse_compute(self):
        for record in self:
            locations = self.env['stock.location'].search([('id','=',record.location_dest_id.id)])
            warehouses = self.env['stock.warehouse'].search([('view_location_id','=',locations.location_id.id)])
            record.warehouse = warehouses.name

    @api.model
    def update_location_dest_id(self):
        self.move_line_ids.write({'location_dest_id':self.location_dest_id}) 
        self.move_line_ids.write({'location_id':self.location_id})

    @api.onchange('picking_type_id', 'partner_id') 
    def onchange_picking_type(self):
        if self.picking_type_id:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id
            elif self.partner_id:
                location_dest_id = self.partner_id.property_stock_customer
            else:
                location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

            if self.state == 'draft' or self.state == 'assigned' or self.state == 'confirmed':
                self.location_id = location_id
                self.location_dest_id = location_dest_id
                
                for move in self.move_ids_without_package:
                    move.location_dest_id = location_dest_id
                    move.location_id = location_id 

                for move_line in self.move_line_ids_without_package:
                    move_line.write({'location_dest_id':self.location_dest_id.id,'location_id':self.location_id.id})
        if self.partner_id and self.partner_id.picking_warn:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in ('no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    self.partner_id = False
                return {'warning': {
                    'title': ("Warning for %s") % partner.name,
                    'message': partner.picking_warn_msg
                }}
        # if stockm:
        #     # stockp = self.env['stock.picking'].search([('move_lines','=',stockm)])
        #     # result = []
        #     # warehouse_ids = self.env['stock.warehouse'].search([('out_type_id','=',self.picking_type_id.id)])
        #     # # result.append((1,self.id,{'warehouse':warehouse_ids}))
        #     # # # stockp.update({'picking_type_id': self.picking_type_id,'location_dest_id':self.location_dest_id.id,'location_id':self.location_id.id})
        #     # self.warehouse = warehouse_ids
        #     # self.action_assign()
        #     self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        #     moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        #     if not moves:
        #         raise UserError(_('Nothing to check the availability for.'))
        #     # If a package level is done when confirmed its location can be different than where it will be reserved.
        #     # So we remove the move lines created when confirmed to set quantity done to the new reserved ones.
        #     package_level_done = self.mapped('package_level_ids').filtered(lambda pl: pl.is_done and pl.state == 'confirmed')
        #     package_level_done.write({'is_done': False})
        #     moves._action_assign()
        #     package_level_done.write({'is_done': True})
        #     return True

    
    
    
    # @api.multi
    # @api.onchange('picking_type_id', 'partner_id') 
    # def onchange_picking_ty(self):
    #     if self.picking_type_code == 'outgoing':
    #         stockm = self.move_ids_without_package.id
    #         for picking in self:
    #             for movel in picking.move_ids_without_package:
    #                 if movel.reserved_availability > 0:
    #                     picking.move_ids_without_package._do_unreserve()
    #                     picking.package_level_ids.filtered(lambda p: not p.move_ids).unlink()
    #                 else:
    #                     pass
    #     if stockm:
    #         stockp = self.env['stock.picking'].search([('move_lines','=',stockm)])
    #         warehouse_id = self.env['stock.warehouse'].search([('out_type_id','=',stockp.picking_type_id.id)])
    #         # stockp.update({'picking_type_id': self.picking_type_id,'location_dest_id':self.location_dest_id.id,'location_id':self.location_id.id})
    #         stockp.update({'warehouse':warehouse_id})
    #         stockp.action_assign()

class StockMove(models.Model):
    _inherit ="stock.move"
    total = fields.Float(string="Total", compute="_total_calculate", readonly=True)

    # @api.one
    # @api.multi
    @api.onchange("product_uom_qty","price_unit")
    def _total_calculate(self):
        for pu in self:
            if pu.price_unit:
                pu.total = pu.price_unit*pu.product_uom_qty
            else:
                pass

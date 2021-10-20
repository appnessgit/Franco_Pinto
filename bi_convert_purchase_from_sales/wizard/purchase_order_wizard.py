# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class createpurchaseorder(models.TransientModel):
	_name = 'create.purchaseorder'
	_description = "Create Purchase Order"

	new_order_line_ids = fields.One2many( 'getsale.orderdata', 'new_order_line_id',string="Order Line")
	partner_id = fields.Many2one('res.partner', string='Vendor', required = True)
	date_order = fields.Datetime(string='Order Date', required=True, copy=False, default=fields.Datetime.now)
	
	@api.model
	def default_get(self,  default_fields):
		res = super(createpurchaseorder, self).default_get(default_fields)
		data = self.env['sale.order'].browse(self._context.get('active_ids',[]))
		update = []
		section_lines = []
		for record in data.order_line:
			# raise UserError(record.display_type)
			if record.display_type == 'line_section':
				# raise UserError(record.name)
				update.append(
					(
						0,
						0,
						{
							"name": record.name,
							"display_type": "line_section",
							# "sequence": data.sequence,
						},
					)
				)
				res.update({'new_order_line_ids': section_lines})
			elif record.display_type != 'line_section':
				update.append((0,0,{
								'product_id' : record.product_id.id,
								'product_uom' : record.product_uom.id,
								'order_id': record.order_id.id,
								'name' : record.name,
								# "display_type": "line_section",
								'product_qty' : record.product_uom_qty,
								'price_unit' : record.price_unit,
								'product_subtotal' : record.price_subtotal,
								}))
		res.update({'new_order_line_ids':update})
		return res

	def action_create_purchase_order(self):
		self.ensure_one()
		res = self.env['purchase.order'].browse(self._context.get('id',[]))
		value = []
		so = self.env['sale.order'].browse(self._context.get('active_id'))
		pricelist = self.partner_id.property_product_pricelist
		partner_pricelist = self.partner_id.property_product_pricelist
		sale_order_name = ""
		so.count= so.count +1
		for data in self.new_order_line_ids:
			sale_order_name = data.order_id.name
			if not sale_order_name:
				sale_order_name = so.name
			final_price = rule_id = False
			if partner_pricelist:
				product_context = dict(self.env.context, partner_id=self.partner_id.id, date=self.date_order, uom=data.product_uom.id)
				if data.product_id:
					final_price, rule_id = partner_pricelist.with_context(product_context).get_product_price_rule(data.product_id, data.product_qty or 1.0, self.partner_id)
			
			else:
				final_price = data.product_id.standard_price
			value.append([0,0,{
								'product_id' : data.product_id.id if data.product_id else False,
								'name' : data.name,
								'product_qty' : data.product_qty ,
								# 'order_id':data.order_id.id if data.order_id else False,
								'product_uom' : data.product_uom.id if data.product_uom else False,
								'taxes_id' : data.product_id.supplier_taxes_id.ids if data.product_id and data.product_id.supplier_taxes_id else False,
								'date_planned' : data.date_planned,
								'price_unit' : final_price,
								'display_type' : data.display_type,
								}])
		res.create({
						'partner_id' : self.partner_id.id,
						'date_order' : str(self.date_order),
						'order_line':value,
						'origin' : sale_order_name,
						'partner_ref' : sale_order_name
					})
		
		return res


class Getsaleorderdata(models.TransientModel):
	_name = 'getsale.orderdata'
	_description = "Get Sale Order Data"

	new_order_line_id = fields.Many2one('create.purchaseorder')
	display_type = fields.Selection([
		('line_section', "Section"),
		('line_note', "Note")], default=False, help="Technical field for UX purpose.")
	product_id = fields.Many2one('product.product', string="Product")
	product_id = fields.Many2one('product.product', string="Product")
	name = fields.Char(string="Description")
	product_qty = fields.Float(string='Quantity', required=True)
	date_planned = fields.Datetime(string='Scheduled Date', default = datetime.today())
	product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
	order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True)
	price_unit = fields.Float(string='Unit Price', digits='Product Price')
	product_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
	
	@api.depends('product_qty', 'price_unit')
	def _compute_total(self):
		for record in self:
			record.product_subtotal = record.product_qty * record.price_unit

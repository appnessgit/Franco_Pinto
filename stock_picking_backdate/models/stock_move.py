from odoo import models, api, fields, _
from odoo.exceptions import UserError

class StockMove(models.Model):
	_inherit = 'stock.move'

	def _set_backdate(self, backdate):
		"""
		set backdate for done stock moves and their conresponding done stock move lines
		"""
		stock_moves = self.filtered(lambda x: x.state == 'done')
		org_price_unit = self._context.get('org_price_unit', False)
		for move in stock_moves:
			if org_price_unit[move.id] > 0:
				move.write({'date': backdate, 'price_unit': org_price_unit[move.id]})
			else:    
				move.write({'date': backdate})

		move_line_ids = self.mapped('move_line_ids').filtered(lambda x: x.state == 'done')
		if move_line_ids:
			move_line_ids.write({'date': backdate})


	def _action_done(self, cancel_backorder=False):
		self.env.context = dict(self.env.context)
		org_value = self._context.get('org_value', False)
		if org_value:
			pass
		else:
			org_qty = {}
			org_price_unit = {}
			org_value = {}
			for record in self:
				move_id = record.id
				org_qty[move_id] = record.product_qty
				org_price_unit[move_id] = record.price_unit
				org_value[move_id] = org_qty[move_id] * org_price_unit[move_id]
			self.env.context.update({
				'org_qty': org_qty,
				'org_price_unit': org_price_unit,
				'org_value': org_value
			})

		res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
		manual_validate_date_time = self._context.get('manual_validate_date_time', False)
		if manual_validate_date_time:
			# print(org_price_unit)
			# raise UserError(_("bisa kin price unit: " + str(org_price_unit)))
			self._set_backdate(manual_validate_date_time)
		return res

	def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
								  cost):
		self.ensure_one()
		AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

		move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
		if move_lines:
			# print('move_lines:')
			# print(move_lines)
			date = self._context.get('force_period_date', fields.Date.context_today(self))
			new_account_move = AccountMove.sudo().create({
				'journal_id': journal_id,
				'line_ids': move_lines,
				'date': date,
				'ref': description,
				'stock_move_id': self.id,
				'stock_valuation_layer_ids': [(6, None, [svl_id])],
				'move_type': 'entry',
			})

			manual_validate_date_time = self._context.get('manual_validate_date_time', False)
			picking_type_code = self._context.get('picking_type_code', False)
			org_value = self._context.get('org_value', False)
			if manual_validate_date_time and picking_type_code == 'incoming':
				purchase_currency_id = self.purchase_line_id.currency_id.id or ''
				# print(purchase_currency_id)
				company_currency_id = self.env.ref('base.main_company').currency_id.id
				if purchase_currency_id != company_currency_id:
					debit_line_ids = new_account_move.line_ids.filtered(lambda x: x.credit == 0)
					if debit_line_ids:
						self.env.cr.execute("""
							UPDATE account_move_line
							SET debit=%s,
							balance=%s
							WHERE id in %s
							""", (
							org_value[self.id],
							org_value[self.id],
							tuple(debit_line_ids.ids)
						))

					credit_line_ids = new_account_move.line_ids.filtered(lambda x: x.debit == 0)
					if credit_line_ids:
						self.env.cr.execute("""
							UPDATE account_move_line
							SET credit=%s,
							balance=-%s
							WHERE id in %s
							""", (
							org_value[self.id],
							org_value[self.id],
							tuple(credit_line_ids.ids)
						))

			new_account_move._post()

	
	def _create_in_svl(self, forced_quantity=None):
		"""Create a `stock.valuation.layer` from `self`.

		:param forced_quantity: under some circunstances, the quantity to value is different than
			the initial demand of the move (Default value = None)
		"""
		svl_vals_list = []
		for move in self:
			move = move.with_context(force_company=move.company_id.id)
			valued_move_lines = move._get_in_move_lines()
			valued_quantity = 0
			for valued_move_line in valued_move_lines:
				valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
			unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
			if move.product_id.cost_method == 'standard':
				unit_cost = move.product_id.standard_price
			svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
			svl_vals.update(move._prepare_common_svl_vals())
			if forced_quantity:
				svl_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
			svl_vals_list.append(svl_vals)
		return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)



	def _get_price_unit(self):
		""" Returns the unit price for the move"""
		result = super(StockMove, self)._get_price_unit()
		self.ensure_one()
		if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
			line = self.purchase_line_id
			order = line.order_id
			price_unit = line.price_unit
			if line.taxes_id:
					price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_void']
			if line.product_uom.id != line.product_id.uom_id.id:
					price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
			if order.currency_id != order.company_id.currency_id:
				# The date must be today, and not the date of the move since the move move is still
				# in assigned state. However, the move date is the scheduled date until move is
				# done, then date of actual move processing. See:
				# https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
				date = order.force_date if order.force_date else fields.Date.context_today(self)
				price_unit = order.currency_id._convert(
					price_unit, order.company_id.currency_id, order.company_id, date, round=False)
			return price_unit
		return result
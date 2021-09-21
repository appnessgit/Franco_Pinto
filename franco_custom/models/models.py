# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError



class franco_custom(models.Model):
    _inherit = 'sale.order'

    def _sales_warehouse_id(self):
        # if self.property_warehouse_id:
        # 	return self.property_warehouse_id
        if self.team_id.wharehouse:
            return self.team_id.wharehouse
        else:
            return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)

    date_order = fields.Datetime(string='Order Date', required=True, readonly=False, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_sales_warehouse_id, check_company=True)

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        # for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
        #     order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

    @api.onchange('team_id')
    def onchange_team_wh(self):
        # raise UserWarning("Test")
        # if self.team_id.wharehouse:
        self.warehouse_id = self.team_id.wharehouse

    three=fields.Boolean('Three hits', default=False, compute='some_method', readonly=True, copy=False)
    count=fields.Integer( store=True)

    # @api.multi
    def some_method(self):

        if self.count == 1:
            self.three = True
        else:
            self.three = False


class franco_custom_purchase(models.Model):
    _inherit = 'purchase.order'
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.company.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            # if order.partner_id not in order.message_partner_ids:
            #     order.message_subscribe([order.partner_id.id])
        return True

class franco_custom_picking(models.Model):
    _inherit = 'stock.picking'


class franco_custom_account_move(models.Model):
    _inherit = 'account.move'


class franco_custom_sale_line(models.Model):
    _inherit = 'sale.order.line'


class franco_custom_purchase_line(models.Model):
    _inherit = 'purchase.order.line'


class franco_custom_account_move_line(models.Model):
    _inherit = 'account.move.line'


class franco_custom_crm_team(models.Model):
    _inherit = 'crm.team'
    wharehouse = fields.Many2one("stock.warehouse")

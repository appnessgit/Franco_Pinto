# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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

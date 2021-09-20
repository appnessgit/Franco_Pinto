# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    force_date = fields.Date(string='Force Date')

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale',
            'date_order': self.force_date if self.force_date else fields.Datetime.now()
        }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    #Field Added
    force_date = fields.Date(string='Force Date')

    def button_approve(self, force=False):
        super(PurchaseOrder, self).button_approve()
        self.write({'state': 'purchase', 'date_approve': self.force_date if self.force_date else fields.Datetime.now()})
        # self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        # return {}
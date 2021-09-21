from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.profiler import profile

class PurchaseOrderInherited(models.Model):
    _inherit = 'purchase.order'

    is_dropship = fields.Boolean("is dropship?")
    so_id = fields.Many2one("sale.order")
    dpi_company = fields.Many2one("res.company",compute='get_other_company',store=True)

    @api.depends('company_id')
    def get_other_company(self):
        for rec in self:
            rec.dpi_company = self.env['res.company'].search([('id','!=',rec.company_id.id)],limit=1).id
    
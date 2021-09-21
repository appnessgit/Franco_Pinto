# Copyright 2018-2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from typing import Sequence
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    show_details = fields.Boolean(string="Show details", default=False)
    show_subtotal = fields.Boolean(string="Show subtotal", default=False)
    test_qty = fields.Float("Quantity")
    test_price = fields.Float("Section Price",store=True)
    test_subtotal = fields.Float("Section Subtotal")
    test_tax = fields.Float("Section Tax")
    sequence = fields.Integer(string='Sequence',index=True)

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line()
        res.update(show_details=self.show_details, show_subtotal=self.show_subtotal)
        return res

    

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    # google_map_partner = fields.Char(string="Map")


    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        for line in result['order_line']:
            if line.display_type == 'line_section':
                price = 0.00
                subtotal = 0.00
                tax = 0.00
                order_lines = self.env['sale.order.line'].search([('id','>',line.id),('order_id','=',line.order_id.id)])
                for ol in order_lines:
                    if ol.display_type != 'line_section':
                        price += ol.price_unit
                        subtotal += ol.price_subtotal
                        tax += ol.price_tax
                    else:
                        break
                if line.test_qty > 0:
                    line.test_price = subtotal / line.test_qty
                else:
                    line.test_price = subtotal
                line.test_subtotal = subtotal
                line.test_tax = tax
        return result

    def write(self, vals):
        res = super(SaleOrder,self).write(vals)
        for line in self.order_line:
            # print("SEQ. xxxxxxxxxxxxxxxxxxxx",line.sequence)
            if line.display_type == 'line_section':
                price = 0.00
                subtotal = 0.00
                tax = 0.00
                sequences = self.env['sale.order.line'].search([('order_id','=',self.id)]).mapped('sequence')
                if line.sequence == 10:
                    order_lines = self.env['sale.order.line'].search([('sequence','=',10),('id','>',line.id),('order_id','=',self.id)])
                else:
                    order_lines = self.env['sale.order.line'].search([('sequence','!=',10),('sequence','>',line.sequence),('order_id','=',self.id)])
                print("ORDER ID =================>",self.id)
                for ol in order_lines:
                    if ol.display_type != 'line_section':
                        # print("OL Price Unit xxxxxxxxxxxxxxxxxxxxxx",ol.price_unit)
                        price += ol.price_unit
                        subtotal += ol.price_subtotal
                        tax += ol.price_tax
                    else:
                        break
                if line.test_qty > 0:
                    print("PRICE ====================>",subtotal)
                    print("QTY ====================>",line.test_qty)
                    line.write({'test_price': subtotal / line.test_qty})
                else:
                    line.write({'test_price': subtotal})
                line.write({'test_subtotal': subtotal})
                line.write({'test_tax': tax})
        return res

    

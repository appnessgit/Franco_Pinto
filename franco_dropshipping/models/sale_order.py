# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.profiler import profile


class sale_order(models.Model):
    _inherit = 'sale.order'
    
    def generate_rfq(self):
        for order in self:
            order.order_line.sudo()._generate_rfqs()

    
class SaleOrderLineDropship(models.Model):
    _inherit = 'sale.order.line'

    def _generate_rfqs(self):
        for line in self:
            PurchaseOrder = self.env['purchase.order']
            if line.product_id:
                suppliers = line.product_id._select_seller(quantity=line.product_uom_qty, uom_id=line.product_uom)
                if not suppliers:
                    raise UserError(_("There is no vendor associated to the product %s. Please define a vendor for this product.") % (line.product_id.display_name,))
                supplierinfo = suppliers[0]
                partner_supplier = supplierinfo.name
                sale_line_purchase_map = {}
                supplier_po_map = {}
                dropship = False
                product_routes = line.route_id or (line.product_id.route_ids + line.product_id.categ_id.total_route_ids)
                for pull_rule in product_routes.mapped('rule_ids'):
                    if pull_rule.picking_type_id.sudo().default_location_src_id.usage == 'supplier' and\
                            pull_rule.picking_type_id.sudo().default_location_dest_id.usage == 'customer':
                        dropship = True
                if line.is_mto or dropship:
                    purchase_order = supplier_po_map.get(partner_supplier.id)

                    po = PurchaseOrder.search([('is_dropship','=',True),
                    ('so_id','=',line.order_id.id),
                    ('partner_id', '=', partner_supplier.id),
                    ('state', '=', 'draft'),
                    ('company_id', '=', line.company_id.id),])
                    if not po:
                        values = line._purchase_dropship_prepare_order_values(supplierinfo)
                        purchase_order = PurchaseOrder.create(values)
                        line_values = line._purchase_dropship_prepare_line_values(purchase_order, quantity=line.product_uom_qty)
                        purchase_line = line.env['purchase.order.line'].create(line_values)
                    else:
                        old_purchase_line = line.env['purchase.order.line'].search([('sale_line_id','=',line.id)])
                        if not old_purchase_line:
                            line_values = line._purchase_dropship_prepare_line_values(po, quantity=line.product_uom_qty)
                            purchase_line = line.env['purchase.order.line'].create(line_values)
                else:
                    purchase_order = supplier_po_map.get(partner_supplier.id)
                    po = PurchaseOrder.search([('is_dropship','=',False),
                    ('so_id','=',line.order_id.id),
                    ('partner_id', '=', partner_supplier.id),
                    ('state', '=', 'draft'),
                    ('company_id', '=', line.company_id.id),])
                    if not po:
                        values = line._purchase_regular_prepare_order_values(supplierinfo)
                        purchase_order = PurchaseOrder.create(values)
                        line_values = line._purchase_dropship_prepare_line_values(purchase_order, quantity=line.product_uom_qty)
                        purchase_line = line.env['purchase.order.line'].create(line_values)
                    else:
                        old_purchase_line = line.env['purchase.order.line'].search([('sale_line_id','=',line.id)])
                        if not old_purchase_line:
                            line_values = line._purchase_dropship_prepare_line_values(po, quantity=line.product_uom_qty)
                            purchase_line = line.env['purchase.order.line'].create(line_values)

    def _purchase_dropship_prepare_order_values(self, supplierinfo):
        """ Returns the values to create the purchase order from the current SO line.
            :param supplierinfo: record of product.supplierinfo
            :rtype: dict
        """
        self.ensure_one()
        partner_supplier = supplierinfo.name
        fpos = self.env['account.fiscal.position'].sudo().get_fiscal_position(partner_supplier.id)
        date_order = self._purchase_get_date_order(supplierinfo)
        picking_type_id = False
        product_routes = self.route_id or (self.product_id.route_ids + self.product_id.categ_id.total_route_ids)
        for pull_rule in product_routes.mapped('rule_ids'):
            if pull_rule.picking_type_id.sudo().default_location_src_id.usage == 'supplier' and\
                    pull_rule.picking_type_id.sudo().default_location_dest_id.usage == 'customer':
                picking_type_id = pull_rule.picking_type_id.id
        if picking_type_id:
            return {
            'partner_id': partner_supplier.id,
            'partner_ref': partner_supplier.ref,
            'so_id': self.order_id.id,
            'is_dropship': True,
            'picking_type_id': picking_type_id or False,
            'company_id': self.company_id.id,
            'currency_id': partner_supplier.property_purchase_currency_id.id or self.env.company.currency_id.id,
            'dest_address_id': partner_supplier.id, # False since only supported in stock
            'origin': self.order_id.name,
            'payment_term_id': partner_supplier.property_supplier_payment_term_id.id,
            'date_order': date_order,
            'fiscal_position_id': fpos.id,
        }
        else:
            return {
                'partner_id': partner_supplier.id,
                'partner_ref': partner_supplier.ref,
                'so_id': self.order_id.id,
                'is_dropship': True,
                # 'picking_type_id': picking_type_id or False,
                'company_id': self.company_id.id,
                'currency_id': partner_supplier.property_purchase_currency_id.id or self.env.company.currency_id.id,
                'dest_address_id': partner_supplier.id, # False since only supported in stock
                'origin': self.order_id.name,
                'payment_term_id': partner_supplier.property_supplier_payment_term_id.id,
                'date_order': date_order,
                'fiscal_position_id': fpos.id,
            }
    
    def _purchase_regular_prepare_order_values(self, supplierinfo):
        """ Returns the values to create the purchase order from the current SO line.
            :param supplierinfo: record of product.supplierinfo
            :rtype: dict
        """
        self.ensure_one()
        partner_supplier = supplierinfo.name
        fpos = self.env['account.fiscal.position'].sudo().get_fiscal_position(partner_supplier.id)
        date_order = self._purchase_get_date_order(supplierinfo)
        return {
            'partner_id': partner_supplier.id,
            'partner_ref': partner_supplier.ref,
            'so_id': self.order_id.id,
            'is_dropship': False,
            'company_id': self.company_id.id,
            'currency_id': partner_supplier.property_purchase_currency_id.id or self.env.company.currency_id.id,
            'dest_address_id': False, # False since only supported in stock
            'origin': self.order_id.name,
            'payment_term_id': partner_supplier.property_supplier_payment_term_id.id,
            'date_order': date_order,
            'fiscal_position_id': fpos.id,
        }
    

    def _purchase_dropship_prepare_line_values(self, purchase_order, quantity=False):
        """ Returns the values to create the purchase order line from the current SO line.
            :param purchase_order: record of purchase.order
            :rtype: dict
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        self.ensure_one()
        # compute quantity from SO line UoM
        product_quantity = self.product_uom_qty
        if quantity:
            product_quantity = quantity

        purchase_qty_uom = self.product_uom._compute_quantity(product_quantity, self.product_id.uom_po_id)

        # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
        # Note: one partner can have multiple supplier info for the same product
        supplierinfo = self.product_id._select_seller(
            partner_id=purchase_order.partner_id,
            quantity=purchase_qty_uom,
            date=purchase_order.date_order and purchase_order.date_order.date(), # and purchase_order.date_order[:10],
            uom_id=self.product_id.uom_po_id
        )
        fpos = purchase_order.fiscal_position_id
        taxes = fpos.map_tax(self.product_id.supplier_taxes_id)
        if taxes:
            taxes = taxes.filtered(lambda t: t.company_id.id == self.company_id.id)

        # compute unit price
        price_unit = 0.0
        if supplierinfo:
            price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price, self.product_id.supplier_taxes_id, taxes, self.company_id)
            if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                price_unit = supplierinfo.currency_id.compute(price_unit, purchase_order.currency_id)

        return {
            'name': '[%s] %s' % (self.product_id.default_code, self.name) if self.product_id.default_code else self.name,
            'product_qty': purchase_qty_uom,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': price_unit,
            'date_planned': fields.Date.from_string(purchase_order.date_order) + relativedelta(days=int(supplierinfo.delay)),
            'taxes_id': [(6, 0, taxes.ids)],
            'order_id': purchase_order.id,
            'sale_line_id': self.id,
        }

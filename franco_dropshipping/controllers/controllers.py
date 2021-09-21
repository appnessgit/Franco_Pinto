# -*- coding: utf-8 -*-
# from odoo import http


# class FrancoDropshipping(http.Controller):
#     @http.route('/franco_dropshipping/franco_dropshipping/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/franco_dropshipping/franco_dropshipping/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('franco_dropshipping.listing', {
#             'root': '/franco_dropshipping/franco_dropshipping',
#             'objects': http.request.env['franco_dropshipping.franco_dropshipping'].search([]),
#         })

#     @http.route('/franco_dropshipping/franco_dropshipping/objects/<model("franco_dropshipping.franco_dropshipping"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('franco_dropshipping.object', {
#             'object': obj
#         })

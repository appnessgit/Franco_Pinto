# -*- coding: utf-8 -*-
# from odoo import http


# class FrancoCustom(http.Controller):
#     @http.route('/franco_custom/franco_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/franco_custom/franco_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('franco_custom.listing', {
#             'root': '/franco_custom/franco_custom',
#             'objects': http.request.env['franco_custom.franco_custom'].search([]),
#         })

#     @http.route('/franco_custom/franco_custom/objects/<model("franco_custom.franco_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('franco_custom.object', {
#             'object': obj
#         })

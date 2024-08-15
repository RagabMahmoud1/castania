# -*- coding: utf-8 -*-
# from odoo import http


# class HrLeaveCustom(http.Controller):
#     @http.route('/hr_leave_custom/hr_leave_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_leave_custom/hr_leave_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_leave_custom.listing', {
#             'root': '/hr_leave_custom/hr_leave_custom',
#             'objects': http.request.env['hr_leave_custom.hr_leave_custom'].search([]),
#         })

#     @http.route('/hr_leave_custom/hr_leave_custom/objects/<model("hr_leave_custom.hr_leave_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_leave_custom.object', {
#             'object': obj
#         })


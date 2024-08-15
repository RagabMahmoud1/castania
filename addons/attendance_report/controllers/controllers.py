# -*- coding: utf-8 -*-
# from odoo import http


# class AttendanceReport(http.Controller):
#     @http.route('/attendance_report/attendance_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/attendance_report/attendance_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('attendance_report.listing', {
#             'root': '/attendance_report/attendance_report',
#             'objects': http.request.env['attendance_report.attendance_report'].search([]),
#         })

#     @http.route('/attendance_report/attendance_report/objects/<model("attendance_report.attendance_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('attendance_report.object', {
#             'object': obj
#         })


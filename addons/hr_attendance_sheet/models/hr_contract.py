# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2020-TODAY .
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, api, tools, _
import babel
import time
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools import format_datetime




class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    att_policy_id = fields.Many2one('hr.attendance.policy', string='Attendance Policy')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leave_id = fields.Many2many('hr.leave', string='Leaves', compute='_get_employee_leaves', store=True)
    attendance_sheet_id = fields.Many2one('attendance.sheet', string='Attendance Sheet', compute='_get_employee_attendance')

    def _get_employee_leaves(self):
        res = {}
        for record in self:
            leaves = self.env['hr.leave'].search([('employee_id', '=', record.id)], limit=1)
            for leave in leaves:
                if leave:
                    res[record.leave_id] = leave.ids
                return res

    def _get_employee_attendance(self):
        for record in self:
            attendances = self.env['attendance.sheet'].search([('employee_id', '=', record.id)], limit=1)
            if attendances:
                record.attendance_sheet_id = attendances
            else:
                record.attendance_sheet_id = False

class HrAttensdance(models.Model):
    _inherit = 'hr.attendance'


    date_from = fields.Date(string='Date From', required=True,
                            default=lambda self: fields.Date.to_string(
                                date.today().replace(day=1)), )  # readonly=True,
    date_to = fields.Date(string='Date To', required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1,
                                                                       days=-1)).date()))  # readonly=True,
    attendance_id = fields.Many2one('attendance.sheet', string='Attendance')






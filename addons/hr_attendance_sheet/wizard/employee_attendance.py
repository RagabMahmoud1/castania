import time
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError, AccessDenied
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp



class EmployeeAttendanceReport(models.TransientModel):
    _name = "employee.attendance.report"
    _description = "attendance_sheet_line_change"

    def _convert_timezone(self, date_time):
        if date_time:
            tz_check_in = date_time + timedelta(hours=3)
            return tz_check_in

    def float_to_hours_minutes(self, float_hours):
        hours = int(float_hours)
        minutes = int((float_hours - hours) * 60)
        round_min = round(minutes)
        return f"{hours}h {round_min}m"

    employee_id = fields.Many2one("hr.employee", string="Employee Name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def _get_data(self):
        total_duration = 0.0
        total_late = 0.0
        total_diff_time = 0.0
        total_over = 0.0
        for rec in self:

            result = []
            time_off = []
            domain = [('employee_id', '=', rec.employee_id.id), ('check_in', '>=', rec.start_date),
                      ('check_out', '<=', rec.end_date)]
            attendance = rec.env['hr.attendance'].search(domain)
            for att in attendance:
                total_duration += att.worked_hours
                total_late += att.late
                total_diff_time += att.leave_before_time
                total_over += att.extra_hours

                res = {
                    'check_in': rec._convert_timezone(att.check_in),
                    'check_out': rec._convert_timezone(att.check_out),
                    'duration': rec.float_to_hours_minutes(att.worked_hours),
                    'late': rec.float_to_hours_minutes(att.late),
                    'diff_time': rec.float_to_hours_minutes(att.leave_before_time + 0.01),
                    'over': rec.float_to_hours_minutes(att.extra_hours),


                }
                result.append(res)

            for emp in rec.employee_id:

                sheet = rec.env['attendance.sheet'].search([('employee_id', '=', rec.employee_id.id), ('date_from', '=', rec.start_date),
                                                            ('date_to', '=', rec.end_date)])
                for s in sheet:
                    leave = rec.env['hr.leave'].search(
                        [('employee_id', '=', rec.employee_id.id), ('request_date_from', '>=', rec.start_date),
                         ('request_date_from', '<=', rec.end_date),  ('state', '=', 'validate')])
                    for l in leave:
                        leave_list = {
                            'time_off': l.holiday_status_id.name,
                            'date_from': l.request_date_from,
                            'date_to': l.request_date_to,
                            'des': l.name
                        }
                        time_off.append(leave_list)
                    datas = {
                        'ids': self,
                        'model': 'employee.attendance.report',
                        'form': result,
                        'leave': time_off,
                        'employee': self.employee_id.name,
                        'employee_id': self.employee_id.id,
                        'department': emp.department_id.name,
                        'job': emp.job_id.name,
                        'start_date': self.start_date,
                        'end_date': self.end_date,
                        'no_absence': s.no_absence,
                        'tot_absence': rec.float_to_hours_minutes(s.tot_absence),
                        'total_duration': rec.float_to_hours_minutes(total_duration),
                        'total_late': rec.float_to_hours_minutes(total_late),
                        'total_diff_time': rec.float_to_hours_minutes(total_diff_time),
                        'total_over': rec.float_to_hours_minutes(total_over),
                    }
                    return datas

    def print_report(self):
        datas = self._get_data()
        return self.env.ref('hr_attendance_sheet.employee_attendance_report').report_action([], data=datas)
from datetime import datetime, timedelta
from odoo import _, api, fields, models, tools
from odoo.addons.resource.models.utils import float_to_time
import pytz
from pytz import timezone, UTC


class hrAttendance(models.Model):
    _inherit = 'hr.attendance'

    late = fields.Float(
        string='Late In',
        compute='_compute_late',
        store=True,
    )

    early = fields.Float(
        string='Overtime',
        compute='_compute_early',
        store=True,
    )

    leave_before_time = fields.Float(
        string='Diff Time',
        compute='_compute_leave_before_time',
        required=False)

    extra_hours = fields.Float(
        string='Extra Hours',
        compute='_compute_extra_hours',
        store=True,
    )
    over_time = fields.Float(
        string='OverTime',
        compute='_compute_over_time',
        store=True,
    )

    hr_payslip_late_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip'
    )

    hr_payslip_leave_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip'
    )

    hr_payslip_early_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip'
    )

    hr_payslip_extra_hours_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip'
    )

    @api.depends('employee_id', 'check_out')
    def _compute_leave_before_time(self):
        for attendance in self:
            if attendance.check_out and attendance.employee_id:
                employee = attendance.employee_id
                check_times = attendance._get_check_time(employee, attendance.check_out)
                if not check_times:
                    continue
                check_ins = check_times.get('check_outs', [])
                tz_check_out = self._convert_timezone(attendance.check_out)
                differences = (check_ins[0] - tz_check_out).total_seconds() / 3600 if check_ins else 0.0
                attendance.leave_before_time = differences if differences >= 0 else 0.0
            else:
                attendance.leave_before_time = 0.0

    def _get_check_time(self, employee_id, check_time):
        check_times = {}
        week_days = dict(self.env['resource.calendar.attendance'].with_context(lang='en_US').fields_get(
            'dayofweek')['dayofweek']['selection'])
        week_days = dict([(value, key) for key, value in week_days.items()])
        resource_calendar = employee_id.resource_calendar_id
        if type(check_time) is datetime:
            check_date = check_time.date()
        else:
            check_date = check_time

        days = resource_calendar.attendance_ids
        day = check_time.strftime('%A')
        week_day = week_days[day]
        days = days.filtered(lambda d: d.dayofweek == week_day)
        if not days:
            return {'check_ins': [], 'check_outs': []}
        check_ins = days.mapped('hour_from')
        check_outs = days.mapped('hour_to')
        check_times.update({
            'check_ins': [datetime.combine(check_date, float_to_time(check_in)) for check_in in check_ins],
            'check_outs': [datetime.combine(check_date, float_to_time(check_out)) for check_out in check_outs]
        })

        return check_times

    def _convert_timezone(self, date_time):
        if date_time:
            # user_tz = self.employee_id.resource_calendar_id.tz or self.env.user.tz or self.env.context.get('tz')
            # user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc

            # tz_check_in = user_pytz.localize(date_time).astimezone(pytz.timezone(self.employee_id._get_tz()))
            # tz_check_in = tz_check_in.replace(tzinfo=None)
            tz_check_in = date_time + timedelta(hours=3)
            return tz_check_in

    @api.depends('employee_id', 'check_in')
    def _compute_late(self):
        for attendance in self:
            if attendance.check_in and attendance.employee_id:
                employee = attendance.employee_id
                check_times = attendance._get_check_time(employee, attendance.check_in)
                if not check_times:
                    continue
                check_ins = check_times.get('check_ins', [])
                tz_check_in = self._convert_timezone(attendance.check_in)
                differences = (tz_check_in - check_ins[0]).total_seconds() / 3600 if check_ins else 0.0
                attendance.late = differences if differences >= 0 else 0.0
            else:
                attendance.late = 0.0

    @api.depends('employee_id', 'check_in')
    def _compute_early(self):
        for attendance in self:
            if attendance.check_in and attendance.employee_id:
                employee = attendance.employee_id
                check_times = attendance._get_check_time(
                    employee, attendance.check_in)
                if not check_times:
                    continue
                check_ins = check_times.get('check_ins', [])
                tz_check_in = self._convert_timezone(attendance.check_in)
                differences = (check_ins[-1] - tz_check_in).total_seconds() / 3600 if check_ins else 0.0
                attendance.early = differences if differences >= 0 else 0.0

            else:
                attendance.early = 0.0

    @api.depends('employee_id', 'check_out')
    def _compute_extra_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.employee_id:
                employee = attendance.employee_id
                check_times = attendance._get_check_time(
                    employee, attendance.check_out)
                if not check_times:
                    continue
                check_outs = check_times.get('check_outs', [])
                tz_check_out = self._convert_timezone(attendance.check_out)
                differences = (check_outs[-1] - tz_check_out).total_seconds() / 3600 if check_outs else 0.0
                attendance.extra_hours = abs(differences) if differences <= 0 else 0.0
            else:
                attendance.extra_hours = 0.0

    @api.depends('extra_hours', 'early')
    def _compute_over_time(self):
        for attendance in self:
            if attendance.extra_hours or attendance.early:
                attendance.over_time = attendance.extra_hours + attendance.early
            else:
                attendance.over_time = False

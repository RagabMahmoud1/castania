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

import pytz
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date
from odoo.tools.float_utils import float_is_zero

import datetime
from odoo.addons.resource.models.utils import float_to_time, HOURS_PER_DAY
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

class HRLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    presence_type_id = fields.Selection([
        ('upl', 'UPL'),
        ('abd', 'ABD'),
        ('aul', 'AUL'),
        ('sna', 'SNA'),
        ('uph', 'UPH'),
    ], string='Presence Type', default=False)
    
        

class AttendanceSheet(models.Model):
    _name = 'attendance.sheet'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Hr Attendance Sheet'
    _order = 'write_date'


    name = fields.Char("name")
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  required=True)

    department_id = fields.Many2one(related='employee_id.department_id',
                                    string='Department', store=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 copy=False, required=True,
                                 default=lambda self: self.env.company,
                                 states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='Date From', required=True,
                            default=lambda self: fields.Date.to_string(
                                date.today().replace(day=1)), )  # readonly=True,
    date_to = fields.Date(string='Date To', required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.datetime.now() + relativedelta(months=+1, day=1,
                                                              days=-1)).date()))  # readonly=True,
    line_ids = fields.One2many(comodel_name='attendance.sheet.line',
                               string='Attendances', readonly=True,
                               inverse_name='att_sheet_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Approved')], default='draft', tracking=True,
        string='Status', required=True, readonly=True, index=True,
        help=' * The \'Draft\' status is used when a HR user is creating a new  attendance sheet. '
             '\n* The \'Confirmed\' status is used when  attendance sheet is confirmed by HR user.'
             '\n* The \'Approved\' status is used when  attendance sheet is accepted by the HR Manager.')
    no_overtime = fields.Integer(compute="_compute_sheet_total",
                                 string="No of overtimes", readonly=True,
                                 store=True)
    tot_overtime = fields.Float(compute="_compute_sheet_total",
                                string="Total Over Time", readonly=True,
                                store=True)
    tot_difftime = fields.Float(compute="_compute_sheet_total",
                                string="Total Diff time Hours", readonly=True,
                                store=True)
    no_difftime = fields.Integer(compute="_compute_sheet_total",
                                 string="No of Diff Times", readonly=True,
                                 store=True)
    tot_late = fields.Float(compute="_compute_sheet_total",
                            string="Total Late In", readonly=True, store=True)
    no_late = fields.Integer(compute="_compute_sheet_total",
                             string="No of Lates",
                             readonly=True, store=True)
    no_absence = fields.Integer(compute="_compute_sheet_total",
                                string="No of Absence Shift", readonly=True,
                                store=True)
    tot_absence = fields.Float(compute="_compute_sheet_total",
                               string="Total absence Hours", readonly=True,
                               store=True)
    tot_worked_hour = fields.Float(compute="_compute_sheet_total",
                                   string="Total Late In", readonly=True,
                                   store=True)
    tot_worked_days = fields.Float(compute="_compute_sheet_total",
                                      string="Total Worked Days", readonly=True,
                                        )
    tot_leave = fields.Float(compute="_compute_sheet_total",
                                   string="Total Leave", readonly=True,
                                   store=True)
    att_policy_id = fields.Many2one(comodel_name='hr.attendance.policy',
                                    string="Attendance Policy ", required=True)
    payslip_id = fields.Many2one(comodel_name='hr.payslip', string='PaySlip')

    contract_id = fields.Many2one('hr.contract', string='Contract',
                                  readonly=True,
                                  states={'draft': [('readonly', False)]})

    is_overtime_approve = fields.Boolean(
        string='Do You Need To Approve Overtime ?')
    is_absent_approve = fields.Boolean(
        string='Do You Need To Approve Absent ?')

    float_overtime = fields.Float(compute='GetFloatOvertime')
    float_absent = fields.Float(compute='GetFloatAbsent')
    absent = fields.Float(string="Absent",  compute='_calculate_attendance_payslip_details', store=True)
    overtime = fields.Float(string="Overtime", compute='_calculate_attendance_payslip_details', store=True)
    time_different = fields.Float(string="Diff Time", compute='_calculate_attendance_payslip_details', store=True)
    latein = fields.Float(string="Late In", compute='_calculate_attendance_payslip_details', store=True)

    @api.onchange('tot_overtime')
    def GetFloatOvertime(self):
        for convert in self:
            x = '{0:02.0f}:{1:02.0f}'.format(*divmod(convert.tot_overtime * 60, 60))
            p = x.replace(':', '.')
            result = float(p)
            convert.float_overtime = result

    def GetFloatAbsent(self):
        for convert in self:
            x = '{0:02.0f}:{1:02.0f}'.format(*divmod(convert.tot_absence * 60, 60))
            p = x.replace(':', '.')
            result = float(p)
            convert.float_absent = result


    @api.constrains('date_from', 'date_to')
    def check_date(self):
        for sheet in self:
            emp_sheets = self.env['attendance.sheet'].search(
                [('employee_id', '=', sheet.employee_id.id),
                 ('id', '!=', sheet.id)])
            for emp_sheet in emp_sheets:
                if max(sheet.date_from, emp_sheet.date_from) < min(
                        sheet.date_to, emp_sheet.date_to):
                    raise UserError(_(
                        'You Have Already Attendance Sheet For That '
                        'Period  Please pick another date !'))

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_approve(self):
        self.write({'state': 'done'})

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        self.name = 'Attendance Sheet - %s - %s' % (self.employee_id.name or '',
                                                    format_date(self.env,
                                                                self.date_from,
                                                                date_format="MMMM y"))
        self.company_id = employee.company_id
        contracts = employee._get_contracts(date_from, date_to)
        if not contracts:
            raise ValidationError(
                _('There Is No Valid Contract For Employee %s' % employee.name))
        self.contract_id = contracts[0]
        if not self.contract_id.att_policy_id:
            raise ValidationError(_(
                "Employee %s does not have attendance policy" % employee.name))
        self.att_policy_id = self.contract_id.att_policy_id

    def write(self, values):
        res = super(AttendanceSheet, self).write(values)
        
        if not self.contract_id:
            if self.employee_id and self.date_from and self.date_to:
                employee = self.employee_id
                date_from = self.date_from
                date_to = self.date_to
                contracts = employee._get_contracts(date_from, date_to)
                if not contracts:
                    raise ValidationError(
                        _('There Is No Valid Contract For Employee %s' % employee.name))
                self.contract_id = contracts[0]
                if not self.contract_id.att_policy_id:
                    raise ValidationError(_(
                        "Employee %s does not have attendance policy" % employee.name))
                self.att_policy_id = self.contract_id.att_policy_id
        return res
    
    @api.depends('line_ids.overtime', 'line_ids.diff_time', 'line_ids.late_in')
    def _compute_sheet_total(self):
        """
        Compute Total overtime,late ,absence,diff time and worked hours
        :return:
        """
        for sheet in self:
            
            # compute tot_worked_days
            worked_days = sheet.line_ids.filtered(lambda l: l.worked_hours > 0)
            sheet.tot_worked_days = len(worked_days)
            # Compute Total Overtime
            overtime_lines = sheet.line_ids.filtered(lambda l: l.overtime > 0)
            sheet.tot_overtime = sum([l.overtime for l in overtime_lines])
            sheet.no_overtime = len(overtime_lines)
            # Compute Total Late In
            late_lines = sheet.line_ids.filtered(lambda l: l.late_in > 0)
            sheet.tot_late = sum([l.late_in for l in late_lines])
            sheet.no_late = len(late_lines)
            # Compute Absence
            absence_lines = sheet.line_ids.filtered(
                lambda l: l.diff_time > 0 and l.status == "ab")
            # sheet.tot_absence = sum([l.diff_time for l in absence_lines])
            hours_per_day = len(absence_lines)
            for rec in sheet.employee_id:
                for work in rec.resource_calendar_id:
                    sheet.tot_absence = work.hours_per_day * sheet.no_absence

            # conmpute earlyout
            diff_lines = sheet.line_ids.filtered(
                lambda l: l.diff_time > 0 and l.status != "ab")
            sheet.tot_difftime = sum([l.diff_time for l in diff_lines])
            sheet.no_difftime = len(diff_lines)
            # Total Leave
            total_leave = sheet.line_ids.filtered(
                lambda l: l.status == "leave")
            sheet.tot_leave = len(total_leave) / 2

    def _get_float_from_time(self, time):
        str_time = datetime.datetime.strftime(time, "%H:%M")
        split_time = [int(n) for n in str_time.split(":")]
        float_time = split_time[0] + split_time[1] / 60.0
        return float_time

    def get_attendance_intervals(self, employee, day_start, day_end, tz):
        """

        :param employee:
        :param day_start:datetime the start of the day in datetime format
        :param day_end: datetime the end of the day in datetime format
        :return:
        """
        day_start_native = day_start.replace(tzinfo=tz).astimezone(
            pytz.utc).replace(tzinfo=None)
        day_end_native = day_end.replace(tzinfo=tz).astimezone(
            pytz.utc).replace(tzinfo=None)
        res = []
        attendances = self.env['hr.attendance'].sudo().search(
            [('employee_id.id', '=', employee.id),
             ('check_in', '>=', day_start_native),
             ('check_in', '<=', day_end_native)],
            order="check_in")
        for att in attendances:
            check_in = att.check_in
            check_out = att.check_out
            if not check_out:
                continue
            res.append((check_in, check_out))
        return res

    def _get_emp_leave_intervals(self, emp, start_datetime=None,
                                 end_datetime=None):
        leaves = []
        leave_obj = self.env['hr.leave']
        leave_ids = leave_obj.search([
            ('employee_id', '=', emp.id),
            ('state', '=', 'validate')])

        for leave in leave_ids:
            date_from = leave.date_from
            if end_datetime and date_from > end_datetime:
                continue
            date_to = leave.date_to
            if start_datetime and date_to < start_datetime:
                continue
            leaves.append((date_from, date_to))
        return leaves

    def get_public_holiday(self, date, emp, start_datetime=None,
                                end_datetime=None):
        public_holiday = []
        # resource.calendar.leaves
        calendar_leave = self.env['resource.calendar.leaves'].sudo().search(
            [('date_from', '<=', date), ('date_to', '>=', date),('resource_id', '=', False)])
        
        if calendar_leave:
            for leave in calendar_leave:
                date_from = leave.date_from
                date_to = leave.date_to
                day_from = date_from.date()
                day_to = date_to.date()
                local_day_from = leave.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp.tz)).date()
                local_day_to = leave.date_to.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp.tz)).date()
                
                current_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                if current_date >= local_day_from and current_date <= local_day_to:
                    public_holiday.append(leave.id)
        
        # public_holidays = self.env['hr.public.holiday'].sudo().search(
        #     [('date_from', '<=', date), ('date_to', '>=', date),
        #         ('state', '=', 'active')])
        # for ph in public_holidays:
        #     print('ph is', ph.name, [e.name for e in ph.emp_ids])
        #     if not ph.emp_ids:
        #         return public_holidays
        #     if emp.id in ph.emp_ids.ids:
        #         public_holiday.append(ph.id)
        return public_holiday

#############################################################################################
    @api.depends('tot_overtime', 'tot_difftime', 'tot_late', 'tot_absence','line_ids.overtime')
    def _calculate_attendance_payslip_details(self):
        for record in self:
            for polciy in record.att_policy_id:
                # LateIn calculation
                for late in polciy.late_rule_id:
                    for latein in late.line_ids:
                        if latein.amount:
                            record.latein = latein.amount * record.tot_late
                        if latein.rate:
                            record.latein = latein.rate * record.tot_late
                # OverTime calculation
                for overtime in polciy.overtime_rule_ids:
                    if overtime.type == "workday":
                        record.overtime = overtime.rate * record.tot_overtime
                    if overtime.type == "weekend":
                        record.overtime = overtime.rate * record.tot_overtime
                    if overtime.type == "ph":
                        record.overtime = overtime.rate * record.tot_overtime

                # Diff Time Calculation
                for diff in polciy.diff_rule_id:
                    for line in diff.line_ids:
                        if line.amount:
                            record.time_different = record.tot_difftime * line.amount
                        if line.rate:
                            record.time_different = record.tot_difftime * line.rate
           	# Absence Calculation
                if record.no_absence <= 5:
                    for absents in polciy.absence_rule_id:
                        for absent in absents.line_ids:
                            for line in record.line_ids:
                                if record.no_absence == 1 and line.status == "ab":
                                    absent_line = self.env['hr.absence.rule.line'].search([('counter', '=', '1'), ('absence_id', '=', absents.id)])
                                    if not absent_line:
                                        record.absent = 0
                                    else:
                                        for rec in absent_line:
                                            record.absent = rec.rate * record.no_absence
                                if record.no_absence == 2 and line.status == "ab":
                                    absent_line = self.env['hr.absence.rule.line'].search([('counter', '=', '2'), ('absence_id', '=', absents.id)])
                                    if not absent_line:
                                        record.absent = 0
                                    else:
                                        for rec in absent_line:
                                            record.absent = rec.rate * record.no_absence
                                if record.no_absence == 3 and line.status == "ab":
                                    absent_line = self.env['hr.absence.rule.line'].search([('counter', '=', '3'), ('absence_id', '=', absents.id)])
                                    if not absent_line:
                                        record.absent = 0
                                    else:
                                        for rec in absent_line:
                                            record.absent = rec.rate * record.no_absence
                                if record.no_absence == 4 and line.status == "ab":
                                    absent_line = self.env['hr.absence.rule.line'].search([('counter', '=', '4'), ('absence_id', '=', absents.id)])
                                    if not absent_line:
                                        record.absent = 0
                                    else:
                                        for rec in absent_line:
                                            record.absent = rec.rate * record.no_absence
                                if record.no_absence == 5 and line.status == "ab":
                                    absent_line = self.env['hr.absence.rule.line'].search([('counter', '=', '5'), ('absence_id', '=', absents.id)])
                                    if not absent_line:
                                        record.absent = 0
                                    else:
                                        for rec in absent_line:
                                            record.absent = rec.rate * record.no_absence

                else:
                    for absents in polciy.absence_rule_id:
                        absent_line = self.env['hr.absence.rule.line'].search(
                            [('counter', '=', '1'), ('absence_id', '=', absents.id)])
                        if not absent_line:
                            record.absent = 0
                        else:
                            for rec in absent_line:
                                record.absent = rec.rate * record.no_absence


    def get_attendances(self):
        for att_sheet in self:
            att_sheet.line_ids.unlink()
            att_line = self.env["attendance.sheet.line"]
            from_date = att_sheet.date_from
            to_date = att_sheet.date_to
            emp = att_sheet.employee_id
            tz = pytz.timezone(emp.tz)
            if not tz:
                raise exceptions.Warning(
                    "Please add time zone for employee : %s" % emp.name)
            calendar_id = emp.contract_id.resource_calendar_id
            if not calendar_id:
                raise ValidationError(_(
                    'Please add working hours to the %s `s contract ' % emp.name))
            policy_id = att_sheet.att_policy_id
            if not policy_id:
                raise ValidationError(_(
                    'Please add Attendance Policy to the %s `s contract ' % emp.name))

            all_dates = [(from_date + timedelta(days=x)) for x in
                         range((to_date - from_date).days + 1)]
            abs_cnt = 0
            for day in all_dates:
                day_start = datetime.datetime(day.year, day.month, day.day)
                day_end = day_start.replace(hour=23, minute=59,
                                            second=59)
                day_str = str(day.weekday())
                date = day.strftime('%Y-%m-%d')
                work_intervals = calendar_id.att_get_work_intervals(day_start,
                                                                    day_end, tz)
                attendance_intervals = self.get_attendance_intervals(emp,
                                                                     day_start,
                                                                     day_end,
                                                                     tz)
                for at_int in attendance_intervals:
                    if at_int[0] == at_int[1]:
                        attendance_intervals.remove(at_int)
                leaves = self._get_emp_leave_intervals(emp, day_start, day_end)
                public_holiday = self.get_public_holiday(date, emp, day_start, day_end)
                reserved_intervals = []
                overtime_policy = policy_id.get_overtime()
                abs_flag = False
                if work_intervals:
                    if public_holiday:
                        if attendance_intervals:
                            for attendance_interval in attendance_intervals:
                                overtime = attendance_interval[1] - \
                                           attendance_interval[0]
                                float_overtime = overtime.total_seconds() / 3600
                                if float_overtime <= overtime_policy[
                                    'ph_after']:
                                    act_float_overtime = float_overtime = 0
                                else:
                                    act_float_overtime = (float_overtime -
                                                          overtime_policy[
                                                              'ph_after'])
                                    float_overtime = (float_overtime -
                                                      overtime_policy[
                                                          'ph_after']) * \
                                                     overtime_policy['ph_rate']
                                ac_sign_in = pytz.utc.localize(
                                    attendance_interval[0]).astimezone(tz)
                                float_ac_sign_in = self._get_float_from_time(
                                    ac_sign_in)
                                ac_sign_out = pytz.utc.localize(
                                    attendance_interval[1]).astimezone(tz)
                                worked_hours = attendance_interval[1] - \
                                               attendance_interval[0]
                                float_worked_hours = worked_hours.total_seconds() / 3600
                                float_ac_sign_out = float_ac_sign_in + float_worked_hours
                                values = {
                                    'date': date,
                                    'day': day_str,
                                    'ac_sign_in': float_ac_sign_in,
                                    'ac_sign_out': float_ac_sign_out,
                                    'worked_hours': float_worked_hours,
                                    # 'o_worked_hours': float_worked_hours,
                                    'overtime': float_overtime,
                                    'act_overtime': act_float_overtime,
                                    'att_sheet_id': self.id,
                                    'status': 'ph',
                                    'note': _("working on Public Holiday")
                                }
                                att_line.create(values)
                        else:
                            values = {
                                'date': date,
                                'day': day_str,
                                'att_sheet_id': self.id,
                                'status': 'ph',
                            }
                            att_line.create(values)
                    else:
                        for i, work_interval in enumerate(work_intervals):
                            float_worked_hours = 0
                            att_work_intervals = []
                            diff_intervals = []
                            late_in_interval = []
                            diff_time = timedelta(hours=00, minutes=00,
                                                  seconds=00)
                            late_in = timedelta(hours=00, minutes=00,
                                                seconds=00)
                            overtime = timedelta(hours=00, minutes=00,
                                                 seconds=00)
                            for j, att_interval in enumerate(
                                    attendance_intervals):
                                if max(work_interval[0], att_interval[0]) < min(
                                        work_interval[1], att_interval[1]):
                                    current_att_interval = att_interval
                                    if i + 1 < len(work_intervals):
                                        next_work_interval = work_intervals[
                                            i + 1]
                                        if max(next_work_interval[0],
                                               current_att_interval[0]) < min(
                                            next_work_interval[1],
                                            current_att_interval[1]):
                                            split_att_interval = (
                                                next_work_interval[0],
                                                current_att_interval[1])
                                            current_att_interval = (
                                                current_att_interval[0],
                                                next_work_interval[0])
                                            attendance_intervals[
                                                j] = current_att_interval
                                            attendance_intervals.insert(j + 1,
                                                                        split_att_interval)
                                    att_work_intervals.append(
                                        current_att_interval)
                            reserved_intervals += att_work_intervals
                            pl_sign_in = self._get_float_from_time(
                                pytz.utc.localize(work_interval[0]).astimezone(
                                    tz))
                            pl_sign_out = self._get_float_from_time(
                                pytz.utc.localize(work_interval[1]).astimezone(
                                    tz))
                            pl_sign_in_time = pytz.utc.localize(
                                work_interval[0]).astimezone(tz)
                            pl_sign_out_time = pytz.utc.localize(
                                work_interval[1]).astimezone(tz)
                            ac_sign_in = 0
                            ac_sign_out = 0
                            status = ""
                            note = ""
                            if att_work_intervals:
                                if len(att_work_intervals) > 1:
                                    # print("there is more than one interval for that work interval")
                                    late_in_interval = (
                                        work_interval[0],
                                        att_work_intervals[0][0])
                                    overtime_interval = (
                                        work_interval[1],
                                        att_work_intervals[-1][1])
                                    if overtime_interval[1] < overtime_interval[0]:
                                        overtime = timedelta(hours=0, minutes=0,
                                                             seconds=0)
                                    else:
                                        overtime = overtime_interval[1] - \
                                                   overtime_interval[0]
                                    remain_interval = (
                                        att_work_intervals[0][1],
                                        work_interval[1])
                                    # print'first remain intervals is',remain_interval
                                    for att_work_interval in att_work_intervals:
                                        float_worked_hours += (
                                                                      att_work_interval[
                                                                          1] -
                                                                      att_work_interval[
                                                                          0]).total_seconds() / 3600
                                        # print'float worked hors is', float_worked_hours
                                        if att_work_interval[1] <= \
                                                remain_interval[0]:
                                            continue
                                        if att_work_interval[0] >= \
                                                remain_interval[1]:
                                            break
                                        if remain_interval[0] < \
                                                att_work_interval[0] < \
                                                remain_interval[1]:
                                            diff_intervals.append((
                                                remain_interval[
                                                    0],
                                                att_work_interval[
                                                    0]))
                                            remain_interval = (
                                                att_work_interval[1],
                                                remain_interval[1])
                                    if remain_interval and remain_interval[0] <= \
                                            work_interval[1]:
                                        diff_intervals.append((remain_interval[
                                                                   0],
                                                               work_interval[
                                                                   1]))
                                    ac_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              0]).astimezone(
                                            tz))
                                    ac_sign_out = self._get_float_from_time(
                                        pytz.utc.localize(
                                            att_work_intervals[-1][
                                                1]).astimezone(tz))
                                    ac_sign_out = ac_sign_in + ((
                                                                        att_work_intervals[
                                                                            -1][
                                                                            1] -
                                                                        att_work_intervals[
                                                                            0][
                                                                            0]).total_seconds() / 3600)
                                else:
                                    late_in_interval = (
                                        work_interval[0],
                                        att_work_intervals[0][0])
                                    overtime_interval = (
                                        work_interval[1],
                                        att_work_intervals[-1][1])
                                    if overtime_interval[1] < overtime_interval[
                                        0]:
                                        overtime = timedelta(hours=0, minutes=0,
                                                             seconds=0)
                                        diff_intervals.append((
                                            overtime_interval[
                                                1],
                                            overtime_interval[
                                                0]))
                                    else:
                                        overtime = overtime_interval[1] - \
                                                   overtime_interval[0]
                                    ac_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              0]).astimezone(
                                            tz))
                                    ac_sign_out = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              1]).astimezone(
                                            tz))
                                    worked_hours = att_work_intervals[0][1] - \
                                                   att_work_intervals[0][0]
                                    float_worked_hours = worked_hours.total_seconds() / 3600
                                    ac_sign_out = ac_sign_in + float_worked_hours
                            else:
                                late_in_interval = []
                                diff_intervals.append(
                                    (work_interval[0], work_interval[1]))

                                status = "ab"
                            if diff_intervals:
                                for diff_in in diff_intervals:
                                    if leaves:
                                        status = "leave"
                                        diff_clean_intervals = calendar_id.att_interval_without_leaves(
                                            diff_in, leaves)
                                        for diff_clean in diff_clean_intervals:
                                            diff_time += diff_clean[1] - \
                                                         diff_clean[0]
                                    else:
                                        diff_time += diff_in[1] - diff_in[0]
                            if late_in_interval:
                                if late_in_interval[1] < late_in_interval[0]:
                                    late_in = timedelta(hours=0, minutes=0,
                                                        seconds=0)
                                else:
                                    if leaves:
                                        late_clean_intervals = calendar_id.att_interval_without_leaves(
                                            late_in_interval, leaves)
                                        for late_clean in late_clean_intervals:
                                            late_in += late_clean[1] - \
                                                       late_clean[0]
                                    else:
                                        late_in = late_in_interval[1] - \
                                                  late_in_interval[0]
                            float_overtime = overtime.total_seconds() / 3600
                            if float_overtime <= overtime_policy['wd_after']:
                                act_float_overtime = float_overtime = 0
                            else:
                                act_float_overtime = float_overtime
                                float_overtime = float_overtime * \
                                                 overtime_policy[
                                                     'wd_rate']
                            float_late = late_in.total_seconds() / 3600
                            act_float_late = late_in.total_seconds() / 3600
                            policy_late = policy_id.get_late(float_late)
                            float_diff = diff_time.total_seconds() / 3600
                            if status == 'ab':
                                if not abs_flag:
                                    abs_cnt += 1
                                abs_flag = True

                                act_float_diff = float_diff
                                float_diff = policy_id.get_absence(float_diff,
                                                                   abs_cnt)
                            else:
                                act_float_diff = float_diff
                                float_diff = policy_id.get_diff(float_diff)
                            values = {
                                'date': date,
                                'day': day_str,
                                'pl_sign_in': pl_sign_in,
                                'pl_sign_out': pl_sign_out,
                                'ac_sign_in': ac_sign_in,
                                'ac_sign_out': ac_sign_out,
                                'late_in': policy_late,
                                'act_late_in': act_float_late,
                                'overtime': float_overtime,
                                'act_overtime': act_float_overtime,
                                'diff_time': float_diff,
                                'act_diff_time': act_float_diff,
                                'status': status,
                                'att_sheet_id': self.id
                            }
                            att_line.create(values)
                        out_work_intervals = [x for x in attendance_intervals if
                                              x not in reserved_intervals]
                        if out_work_intervals:
                            for att_out in out_work_intervals:
                                overtime = att_out[1] - att_out[0]
                                ac_sign_in = self._get_float_from_time(
                                    pytz.utc.localize(att_out[0]).astimezone(
                                        tz))
                                ac_sign_out = self._get_float_from_time(
                                    pytz.utc.localize(att_out[1]).astimezone(
                                        tz))
                                float_worked_hours = overtime.total_seconds() / 3600
                                ac_sign_out = ac_sign_in + float_worked_hours
                                float_overtime = overtime.total_seconds() / 3600
                                if float_overtime <= overtime_policy[
                                    'wd_after']:
                                    float_overtime = act_float_overtime = 0
                                else:
                                    act_float_overtime = float_overtime
                                    float_overtime = act_float_overtime * \
                                                     overtime_policy['wd_rate']
                                values = {
                                    'date': date,
                                    'day': day_str,
                                    'pl_sign_in': 0,
                                    'pl_sign_out': 0,
                                    'ac_sign_in': ac_sign_in,
                                    'ac_sign_out': ac_sign_out,
                                    'overtime': float_overtime,
                                    'worked_hours': float_worked_hours,
                                    'act_overtime': act_float_overtime,
                                    'note': _("overtime out of work intervals"),
                                    'att_sheet_id': self.id
                                }
                                att_line.create(values)
                else:
                    if attendance_intervals:
                        # print "thats weekend be over time "
                        for attendance_interval in attendance_intervals:
                            overtime = attendance_interval[1] - \
                                       attendance_interval[0]
                            ac_sign_in = pytz.utc.localize(
                                attendance_interval[0]).astimezone(tz)
                            ac_sign_out = pytz.utc.localize(
                                attendance_interval[1]).astimezone(tz)
                            float_overtime = overtime.total_seconds() / 3600
                            # get the day name
                            day_name = day.strftime('%A')
                            if day_name == 'Sunday':
                                _after = overtime_policy['su_after']
                                _rate = overtime_policy['su_rate']
                            elif day_name == 'Saturday':
                                _after = overtime_policy['sa_after']
                                _rate = overtime_policy['sa_rate']
                            else:
                                _after = overtime_policy['we_after']
                                _rate = overtime_policy['we_rate']
                                
                            if float_overtime <= _after:
                                float_overtime = 0
                                act_float_overtime = 0
                            else:
                                act_float_overtime = float_overtime
                                float_overtime = act_float_overtime * \
                                                    _rate
                            ac_sign_in = pytz.utc.localize(
                                attendance_interval[0]).astimezone(tz)
                            ac_sign_out = pytz.utc.localize(
                                attendance_interval[1]).astimezone(tz)
                            worked_hours = attendance_interval[1] - \
                                           attendance_interval[0]
                            float_worked_hours = worked_hours.total_seconds() / 3600
                            values = {
                                'date': date,
                                'day': day_str,
                                'ac_sign_in': self._get_float_from_time(ac_sign_in),
                                'ac_sign_out': self._get_float_from_time(
                                    ac_sign_out),
                                'overtime': float_overtime,
                                'act_overtime': act_float_overtime,
                                'worked_hours': float_worked_hours,
                                'att_sheet_id': self.id,
                                'status': 'weekend',
                                'note': _("working in weekend")
                            }
                            att_line.create(values)
                    else:
                        values = {
                            'date': date,
                            'day': day_str,
                            'att_sheet_id': self.id,
                            'status': 'weekend',
                            'note': ""
                        }
                        att_line.create(values)

    def action_payslip(self):
        self.ensure_one()
        payslip_id = self.payslip_id
        if not payslip_id:
            payslip_id = self.create_payslip()[0]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': payslip_id.id,
            'views': [(False, 'form')],
        }

    def action_create_overtime(self):
        if self.float_overtime == 0.0:
            raise ValidationError(_(
                "There is no Overtime Hours To Approve You Have To Click on Approve With out Or Review Overtime Rule Rate!"))
        else:
            x = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.tot_overtime * 60, 60))
            p = x.replace(':', '.')
            result = float(p)
            return {
                'name': _("Create Overtime"),
                'view_mode': 'form',
                'view_id': self.env.ref("smt_hr_incentive_deduction.hr_overtime_form_view").id,
                'res_model': 'hr.overtime.allowance',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_employee_id': self.employee_id.id,
                    'default_overtime_no_hours': result,
                    'default_overtime_due_date': fields.Date.today(),
                }
            }

    def action_approve_ded(self):
        if self.float_absent == 0.0:
            raise ValidationError(_(
                "There is no Absence Hours To Approve You Have To Click on Approve With out Or Review Absence Rule Rate!"))
        else:
            x = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.tot_absence * 60, 60))
            p = x.replace(':', '.')
            result = float(p)
            return {
                'name': _("Create Absent"),
                'view_mode': 'form',
                'view_id': self.env.ref("smt_hr_incentive_deduction.hr_absent_form_view").id,
                'res_model': 'hr.absent',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': {
                    'default_employee_id': self.employee_id.id,
                    'default_number_of_absent': self.tot_absence,
                    'default_type': "hour",

                }
            }



    def _get_workday_lines(self):
        self.ensure_one()
        contract = self.contract_id.id
        work_enty_obj = self.env['hr.work.entry.type']
        work_entry_types = self.contract_id.structure_type_id.default_struct_id.unpaid_work_entry_type_ids
        if not work_entry_types:
            raise ValidationError(_(
                "Please Add Unpaid Work Entry To %s Salary Structure" % self.contract_id.name))

        work_entry_type = work_entry_types[0]

        overtime_work_entry = work_enty_obj.search([('code', '=', 'ATTSHOT')])
        latin_work_entry = work_enty_obj.search([('code', '=', 'ATTSHLI')])
        absence_work_entry = work_enty_obj.search([('code', '=', 'ATTSHAB')])
        difftime_work_entry = work_enty_obj.search([('code', '=', 'ATTSHDT')])
        if not overtime_work_entry:
            raise ValidationError(_(
                'Please Add Work Entry Type For Attendance Sheet Overtime With Code ATTSHOT'))
        if not latin_work_entry:
            raise ValidationError(_(
                'Please Add Work Entry Type For Attendance Sheet Late In With Code ATTSHLI'))
        if not absence_work_entry:
            raise ValidationError(_(
                'Please Add Work Entry Type For Attendance Sheet Absence With Code ATTSHAB'))
        if not difftime_work_entry:
            raise ValidationError(_(
                'Please Add Work Entry Type For Attendance Sheet Diff Time With Code ATTSHDT'))

        overtime = [{
            'name': "Overtime",
            'code': 'OVT',
            'work_entry_type_id': overtime_work_entry[0].id,
            'sequence': 30,
            'number_of_days': self.no_overtime,
            'number_of_hours': self.tot_overtime,
        }]
        absence = [{
            'name': "Absence",
            'code': 'ABS',
            'work_entry_type_id': absence_work_entry[0].id,
            'sequence': 35,
            'number_of_days': self.no_absence,
            'number_of_hours': self.tot_absence,
        }]
        late = [{
            'name': "Late In",
            'code': 'LATE',
            'work_entry_type_id': latin_work_entry[0].id,
            'sequence': 40,
            'number_of_days': self.no_late,
            'number_of_hours': self.tot_late,
        }]
        difftime = [{
            'name': "Difference time",
            'code': 'DIFFT',
            'work_entry_type_id': difftime_work_entry[0].id,
            'sequence': 45,
            'number_of_days': self.no_difftime,
            'number_of_hours': self.tot_difftime,
        }]
        worked_days_lines = overtime + late + absence + difftime
        return worked_days_lines

    def create_payslip(self):
        payslips = self.env['hr.payslip']
        for att_sheet in self:
            if att_sheet.payslip_id:
                continue
            from_date = att_sheet.date_from
            to_date = att_sheet.date_to
            employee = att_sheet.employee_id
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date,
                                                                    to_date,
                                                                    employee.id,
                                                                    contract_id=False)
            contract_id = slip_data['value'].get('contract_id')
            if not contract_id:
                raise exceptions.Warning(
                    'There is No Contracts for %s That covers the period of the Attendance sheet' % employee.name)
            worked_days_line_ids = slip_data['value'].get(
                'worked_days_line_ids')

            overtime = [{
                'name': "Overtime",
                'code': 'OVT',
                'contract_id': contract_id,
                'sequence': 30,
                'number_of_days': att_sheet.no_overtime,
                'number_of_hours': att_sheet.tot_overtime,
            }]
            absence = [{
                'name': "Absence",
                'code': 'ABS',
                'contract_id': contract_id,
                'sequence': 35,
                'number_of_days': att_sheet.no_absence,
                'number_of_hours': att_sheet.tot_absence,
            }]
            late = [{
                'name': "Late In",
                'code': 'LATE',
                'contract_id': contract_id,
                'sequence': 40,
                'number_of_days': att_sheet.no_late,
                'number_of_hours': att_sheet.tot_late,
            }]
            difftime = [{
                'name': "Difference time",
                'code': 'DIFFT',
                'contract_id': contract_id,
                'sequence': 45,
                'number_of_days': att_sheet.no_difftime,
                'number_of_hours': att_sheet.tot_difftime,
            }]
            worked_days_line_ids += overtime + late + absence + difftime

            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': contract_id,
                'input_line_ids': [(0, 0, x) for x in
                                   slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in
                                         worked_days_line_ids],
                'date_from': from_date,
                'date_to': to_date,
            }
            new_payslip = self.env['hr.payslip'].create(res)
            att_sheet.payslip_id = new_payslip
            payslips += new_payslip
        return payslips


class AttendanceSheetLine(models.Model):
    _name = 'attendance.sheet.line'
    _description = "attendance_sheet_line"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sum', 'Summary'),
        ('confirm', 'Confirmed'),
        ('done', 'Approved')], related='att_sheet_id.state', store=True, )

    date = fields.Date("Date")
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, )
    
    day_name = fields.Char("Day Name", compute='_compute_day_name')
    @api.depends('day')
    def _compute_day_name(self):
        for rec in self:
            rec.day_name = dict(self._fields['day'].selection).get(rec.day)
    att_sheet_id = fields.Many2one(comodel_name='attendance.sheet',
                                   ondelete="cascade",
                                   string='Attendance Sheet', readonly=True)
    employee_id = fields.Many2one(related='att_sheet_id.employee_id',
                                  string='Employee')
    pl_sign_in = fields.Float("Planned sign in", readonly=True)
    pl_sign_out = fields.Float("Planned sign out", readonly=True)
    pl_work_hours = fields.Float("Planned Work Hours", readonly=True, compute='_compute_pl_work_hours')
    
    @api.depends('pl_sign_in', 'pl_sign_out')
    def _compute_pl_work_hours(self):
        for rec in self:
            if rec.pl_sign_in and rec.pl_sign_out:
                delta = rec.pl_sign_out - rec.pl_sign_in
                rec.pl_work_hours = delta
            else:
                rec.pl_work_hours = False
                
    worked_hours = fields.Float(string="Worked Hours", readonly=True, compute='_calculate_attendance_type_details')
    overtime = fields.Float("Overtime", readonly=True, store=True)
    late_in = fields.Float("Late In", readonly=True, store=True)
    ac_sign_in = fields.Float(string="Actual sign in", compute='_get_acutal_in_out', store=True)
    ac_sign_out = fields.Float(string="Actual sign out", compute='_get_acutal_in_out', store=True)
    overtime = fields.Float("Overtime", readonly=True, store=True)
    act_overtime = fields.Float("Actual Overtime", readonly=True)
    late_in = fields.Float("Late In", readonly=True,  store=True)
    diff_time = fields.Float("Diff Time",
                             help="Diffrence between the working time and attendance time(s) ",
                             readonly=True, store=True)
    act_late_in = fields.Float("Actual Late In", readonly=True)
    act_diff_time = fields.Float("Actual Diff Time",
                                 help="Diffrence between the working time and attendance time(s) ",
                                 readonly=True)
    status = fields.Selection(string="Status",
                              selection=[('workday', 'Working Day'),
                                         ('ab', 'Absence'),
                                         ('weekend', 'Week End'),
                                         ('ph', 'Public Holiday'),
                                         ('leave', 'Leave'), ],
                              required=False)
    note = fields.Text("Note")
    
    # abs   .Absence Hourly
    # anl   .Annual Leave
    # ovs   .Overtime SAT
    # ov1   .OVT 1
    # ovh
    # prs   .Presence
    # upl   .Unpaid Leave
    # abd   .Absence Daily
    # aul   Authorized Leave
    # sna   .Sick Leave not approved
    # uph   UNPAID HOURS
    abs = fields.Float("Absence", readonly=True, compute='_calculate_attendance_type_details')
    anl = fields.Float("Annual Leave", readonly=True, compute='_calculate_attendance_type_details')
    ovs = fields.Float("Overtime SAT", readonly=True, compute='_calculate_attendance_type_details')
    ov1 = fields.Float("OVT 1", readonly=True, compute='_calculate_attendance_type_details')
    ovh = fields.Float("Overtime Hours", readonly=True, compute='_calculate_attendance_type_details')
    prs = fields.Float("Presence", readonly=True, compute='_calculate_attendance_type_details')
    upl = fields.Float("Unpaid Leave", readonly=True, compute='_calculate_attendance_type_details')
    abd = fields.Float("Absence Daily", readonly=True, compute='_calculate_attendance_type_details')
    aul = fields.Float("Authorized Leave", readonly=True, compute='_calculate_attendance_type_details')
    sna = fields.Float("Sick Leave not approved", readonly=True, compute='_calculate_attendance_type_details')
    uph = fields.Float("UNPAID HOURS", readonly=True, compute='_calculate_attendance_type_details')
    ovt = fields.Float("Overtime", readonly=True, compute='_calculate_attendance_type_details')
    status_leave = fields.Char("Status Leave", compute='_calculate_attendance_type_details')
    
    def get_leave_day_hour(self, leave):
        leave_type = leave.holiday_status_id
        request_unit = leave_type.request_unit
        if request_unit in ['hour', 'half_day']:
            return leave.number_of_hours
        else:
            return False

    
    @api.depends('late_in','diff_time','overtime', 'status')
    def _calculate_attendance_type_details(self):
        for record in self:
            
            record.worked_hours = record.ac_sign_out - record.ac_sign_in
            record.status_leave = ''
            record.abs = 0.0    
            record.anl = 0.0        
            record.ovs = 0.0
            record.ov1 = 0.0        
            record.ovh = 0.0    
            record.prs = 0.0    
            record.upl = 0.0
            record.abd = 0.0
            record.aul = 0.0        
            record.sna = 0.0
            record.ovt = 0.0
            record.uph = 0.0
            
            if record.status == 'ab':
                record.abs = record.pl_work_hours
                
            if record.overtime:
                if record.status in ['weekend']:
                    # check the day name
                    day_name = record.date.strftime('%A')
                    if day_name == 'Sunday':
                        record.ovh = record.overtime
                    else:
                        record.ovs = record.overtime
                elif record.status in ['ph']:
                    record.ovh = record.overtime 
                else:       
                    record.ovt = record.overtime
            
            record.prs = record.worked_hours - record.act_overtime
            
            # # public_holiday = self.env['resource.calendar.leaves'].search([('date_from', '<=', record.date), ('date_to', '>=', record.date)])
            # public_holiday = self.env['hr.holidays.public.line'].search([('date', '=', record.date)])
            date = record.date.strftime('%Y-%m-%d')
            public_holiday = self.get_public_holiday(date, record.employee_id)
            leave = self.env['hr.leave'].search([('employee_id', '=', record.employee_id.id), ('date_from', '<=', record.date), ('date_to', '>=', record.date), ('state', '=', 'validate')])
            if record.status == 'leave' or leave:
                # get the leave type
                if leave:
                    if leave.holiday_status_id.presence_type_id:
                        record.status_leave = leave.holiday_status_id.presence_type or ''
                        if leave.holiday_status_id.presence_type_id == "upl":
                            record.upl = record.get_leave_day_hour(leave) or record.pl_work_hours
                        elif leave.holiday_status_id.presence_type_id == "abd":
                            record.abd = record.get_leave_day_hour(leave) or record.pl_work_hours
                        elif leave.holiday_status_id.presence_type_id == "aul":
                            record.aul = record.get_leave_day_hour(leave) or record.pl_work_hours
                        elif leave.holiday_status_id.presence_type_id == "sna":
                            record.sna = record.get_leave_day_hour(leave) or record.pl_work_hours
                        elif leave.holiday_status_id.presence_type_id == "uph":
                            record.uph = record.get_leave_day_hour(leave) or record.pl_work_hours
                        
                    else:
                        record.anl = record.get_leave_day_hour(leave) or record.pl_work_hours
            else:
                record.anl = 0.0
                record.sna = 0.0
                record.upl = 0.0
                record.aul = 0.0
                record.uph = 0.0
                record.ov1 = 0.0
                record.upl = 0.0
                
                record.abs = record.diff_time + record.late_in
                
            
            if record.status == 'ph' or public_holiday:
                
                record.ovh = record.overtime
                record.status = 'ph'
                if public_holiday and len(public_holiday) > 0:
                    if public_holiday[0]:
                        record.status_leave =  public_holiday[0] or 'Public Holiday'
                    
                record.ovt = 0.0
                record.ovs = 0.0
                record.prs = 0.0
                record.abd = 0.0
                record.anl = 0.0
                record.sna = 0.0
                record.upl = 0.0
                record.aul = 0.0
                record.uph = 0.0
                record.ov1 = 0.0
                record.abs = 0.0
            
            # check Absence
            if record.status == 'ab':
                record.abd = record.pl_work_hours
                record.status_leave = 'Absence'

    @api.depends('ac_sign_in', 'ac_sign_out')
    def _get_acutal_in_out(self):
        for rec in self:
            if rec.ac_sign_in and rec.ac_sign_out:
                rec.ac_sign_in = rec.ac_sign_in
                rec.ac_sign_out = rec.ac_sign_out


    def get_public_holiday(self, date, emp, start_datetime=None,
                                end_datetime=None):
        public_holiday = []
        # resource.calendar.leaves
        calendar_leave = self.env['resource.calendar.leaves'].sudo().search([('date_from', '<=', date), ('date_to', '>=', date),('resource_id', '=', False)])
        
        if calendar_leave:
            for leave in calendar_leave:
                date_from = leave.date_from
                date_to = leave.date_to
                day_from = date_from.date()
                day_to = date_to.date()
                local_day_from = leave.date_from.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp.tz)).date()
                local_day_to = leave.date_to.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(emp.tz)).date()
                
                current_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                if current_date >= local_day_from and current_date <= local_day_to:
                    public_holiday.append(leave.presence_type)
        
        # public_holidays = self.env['hr.public.holiday'].sudo().search(
        #     [('date_from', '<=', date), ('date_to', '>=', date),
        #         ('state', '=', 'active')])
        # for ph in public_holidays:
        #     print('ph is', ph.name, [e.name for e in ph.emp_ids])
        #     if not ph.emp_ids:
        #         return public_holidays
        #     if emp.id in ph.emp_ids.ids:
        #         public_holiday.append(ph.id)
        return public_holiday    
    # @api.depends('ac_sign_in', 'ac_sign_out')
    # def _compute_worke_hours(self):
    #     for attendance in self:

    #         if attendance.ac_sign_out and attendance.ac_sign_in:
    #             delta = attendance.ac_sign_out - attendance.ac_sign_in
    #             attendance.worked_hours = delta
    #         else:
    #             attendance.worked_hours = False
    #          # OverTime
    #         over = attendance.ac_sign_out - attendance.pl_sign_out
    #         if attendance.pl_sign_in > attendance.ac_sign_in:
    #             early = attendance.pl_sign_in - attendance.ac_sign_in
    #         else:
    #             early = False
    #         attendance.overtime = (over + early) - attendance.late_in

    #         if attendance.overtime < 0.0:
    #             attendance.overtime = False
                
    #         # LateIn
    #         if attendance.ac_sign_in > attendance.pl_sign_in:
    #             late = attendance.ac_sign_in - attendance.pl_sign_in
    #             attendance.late_in = late
    #         else:
    #             attendance.late_in = False
    #         # Diff Time
    #         if attendance.ac_sign_out < attendance.pl_sign_out and attendance.status != 'ab' and attendance.status != 'leave':
    #             diff = attendance.pl_sign_out - attendance.ac_sign_out
    #             attendance.diff_time = diff
    #         else:
    #             attendance.diff_time = False

    #         if not attendance.pl_sign_in and attendance.pl_sign_out:
    #             attendance.status = 'weekend'




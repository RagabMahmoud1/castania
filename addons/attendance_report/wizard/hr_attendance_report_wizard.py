# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from datetime import timedelta, datetime
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrAttendanceReportWizard(models.TransientModel):
    _name = 'hr.attendance.report.wizard'
    _description = _('HrAttendanceReportWizard')

    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    contract_id = fields.Many2one('hr.contract', string='Contract', related='employee_id.contract_id', store=True)
    working_schedule_id = fields.Many2one('resource.calendar', string='Working Schedule', compute='_compute_working_schedule_id', store=True)
    daily_report = fields.Many2one('hr.daily.attendance.report', string='Daily Report')
    daily_report_lines = fields.One2many('hr.daily.attendance.report.lines', 'attendance_report_id', string='Daily Report Lines')
    
    
    def _compute_working_schedule_id(self):
        for rec in self:
            rec.working_schedule_id = rec.contract_id.resource_calendar_id.id
    
    def print(self):
        self.ensure_one()

        if not self.employee_id:
            raise ValidationError(_('Please select an employee.'))
        if not self.date_from:
            raise ValidationError(_('Please select a date from.'))
        if not self.date_to:
            raise ValidationError(_('Please select a date to.'))
        
        # Create a new record in the hr.daily.attendance.report model
        daily_report = self.env['hr.daily.attendance.report'].create({
            'employee_id': self.employee_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'contract_id': self.contract_id.id,
            'working_schedule_id': self.working_schedule_id.id,
            # 'line_ids': self.compute_attendance_report_lines(),
            'line_ids2': self.compute_attendance_report_lines2()
        })
        
        # return the daily report as pdf reprt   action action_report_hr_daily_attendance
        action_report = self.env.ref('attendance_report.action_report_hr_daily_attendance').report_action(daily_report)
        
        return action_report
        

    def compute_attendance_report_lines2(self):
        self.ensure_one()
        
        attendance_report_lines2 = []
        
        line_ids2 = self.env['hr.daily.attendance.report.lines2']
        
        # loop through the selected date range
        all_days_list = [self.date_from + timedelta(days=x) for x in range((self.date_to - self.date_from).days + 1)]
        leaves = self.env['hr.leave'].search([
                ('employee_id', '=', self.employee_id.id),
                ('request_date_from', '<=', self.date_to),
                ('request_date_to', '>=', self.date_from),
                ('state', '=', 'validate'),
                
            ])
        for day in all_days_list:
            date_from = day.strftime('%Y-%m-%d 00:00:00')
            date_to = day.strftime('%Y-%m-%d 23:59:59')
            
            # get the attendance record for the selected employee and date
            attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('check_in', '>=', date_from),
                ('check_in', '<=', date_to),
            ])
                
            
            # get the booking in and booking out time
            if not attendance:
                booking_in = False
                booking_out = False
                # get the cumulative
                cumulative = timedelta(hours=0)
                float_cumulative = 0.0
            else:
                booking_in = attendance[0].check_in
                booking_out = attendance[0].check_out
                # get the cumulative
                cumulative = booking_out - booking_in
                float_cumulative = cumulative.total_seconds() / 3600
                

            # get the status
            status = ''
            
            
            
            # get the duty from and duty to time
            calender = self.contract_id.resource_calendar_id
            calendar_attendance = calender.attendance_ids.filtered(lambda x: x.dayofweek == str(day.weekday()))
            
            # convert hour_from float to datetime 7.5 -> 07:30:00
            converted_hour_from = timedelta(hours=calendar_attendance.hour_from)
            duty_from = datetime.combine(day,  datetime.min.time()) + converted_hour_from 
            
            # convert hour_to float to datetime 16.5 -> 16:30:00
            converted_hour_to = timedelta(hours=calendar_attendance.hour_to)
            duty_to = datetime.combine(day, datetime.min.time()) + converted_hour_to
            
            # get the number of hours
            number_of_hours = calendar_attendance.hour_to - calendar_attendance.hour_from
            
            # get the abs
            abs = 0
            if float_cumulative < number_of_hours:
                abs = number_of_hours - float_cumulative
            
            # get the anl
            anl = 0
            
            if leaves:
                leave = leaves.filtered(lambda x: x.request_date_from <= day and x.request_date_to >= day)
                if leave:
                    anl = leave.number_of_hours
            
            # get the ovs
            ovs = 0
            over_time = 0
            if float_cumulative > number_of_hours:
                over_time = float_cumulative - number_of_hours
                ovs = over_time
            
            
            # get the ov1
            ov1 = 0
            ov1 = over_time
            # get the ovh
            ovh = 0
            ovh = over_time
            
            
            # get the prs
            prs = 0
            
            # get the upl
            upl = 0 # unpaid leave
            if leaves:
                leave = leaves.filtered(lambda x: x.request_date_from <= day and x.request_date_to >= day and x.holiday_status_id.unpaid)
                if leave:
                    upl = leave.number_of_hours
            
            # get the abd
            abd = 0 # Absence Day
            if float_cumulative < number_of_hours:
                abd = number_of_hours - float_cumulative
            
            # get the aul
            aul = 0 # Authorized Leave
            if leaves:
                leave = leaves.filtered(lambda x: x.request_date_from <= day and x.request_date_to >= day)
                if leave:
                    aul = leave.number_of_hours

            
            # get the sna
            sna = 0
            
            # get the uph
            uph = 0
            
            # get the total
            total = 0
            
            # compute status : Official Holiday,Duty Off, Assigned absence annual
            if abs > 0:
                status = "Absence Day"
                
            if not calendar_attendance:
                status = "Duty Off"
            
            if leaves:
                leave = leaves.filtered(lambda x: x.request_date_from <= day and x.request_date_to >= day)
                if leave:
                    status = "Assigned absence annual"
            
                
            vals_list = {
                'employee_id': self.employee_id.id,
                'date': day,
                'booking_in': booking_in,
                'booking_out': booking_out,
                'cumulative': float_cumulative,
                'status': status,
                'duty_from': duty_from,
                'duty_to': duty_to,
                'number_of_hours': number_of_hours,
                'abs': abs,
                'anl': anl,
                'ovs': ovs,
                'ov1': ov1,
                'ovh': ovh,
                'prs': prs,
                'upl': upl,
                'abd': abd,
                'aul': aul,
                'sna': sna,
                'uph': uph,
                'total': total
            }
            
            res = line_ids2.create(vals_list)
            line_ids2 += res
            
        return line_ids2
        
# class attendance_report(models.Model):
class HrAttendanceReport(models.Model):
    _name = 'hr.daily.attendance.report'
    _description = _('HrAttendanceReport')
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    contract_id = fields.Many2one('hr.contract', string='Contract', related='employee_id.contract_id', store=True)
    working_schedule_id = fields.Many2one('resource.calendar', string='Working Schedule', compute='_compute_working_schedule_id', store=True)
    line_ids = fields.One2many('hr.daily.attendance.report.lines', 'attendance_report_id', string='Lines')
    line_ids2 = fields.One2many('hr.daily.attendance.report.lines2', 'attendance_report_id', string='Lines')
    
    def _compute_working_schedule_id(self):
        for rec in self:
            rec.working_schedule_id = rec.contract_id.resource_calendar_id.id
    
    def print(self):
        _logger.info('Hello Report')



# class attendance_report_lines(models.Model):       
class HrAttendanceReportLines(models.Model):
    _name = 'hr.daily.attendance.report.lines'
    _description = _('HrAttendanceReportLines')
    
    attendance_report_id = fields.Many2one('hr.daily.attendance.report', string='Attendance Report')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date = fields.Date(string='Date')
    planned_check_in = fields.Datetime(string='Planned Check In')
    planned_check_out = fields.Datetime(string='Planned Check Out')
    planned_work_hours = fields.Float(string='Number of Hours')
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    working_hours = fields.Float(string='Working Hours')
    late = fields.Float(string='Late In')
    early = fields.Float(string='Overtime')
    leave_before_time = fields.Float(string='Diff Time')
    extra_hours = fields.Float(string='Extra Hours')
    over_time = fields.Float(string='OverTime')
    
    def print(self):
        _logger.info('Hello Report Line')
        
        
class HrAttendanceReportLines2(models.Model):
    _name = 'hr.daily.attendance.report.lines2'
    _description = _('HrAttendanceReportLines2')
    
    attendance_report_id = fields.Many2one('hr.daily.attendance.report', string='Attendance Report')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date = fields.Date(string='Date')
    booking_in = fields.Datetime(string='Booking In')
    booking_out = fields.Datetime(string='Booking Out')
    cumulative = fields.Float(string='Cumulative')
    status = fields.Char(string='Status')
    duty_from = fields.Datetime(string='Duty From')
    duty_to = fields.Datetime(string='Duty To')
    number_of_hours = fields.Float(string='Number of Hours')
    abs = fields.Float(string='Abs')
    anl = fields.Float(string='Anl')
    ovs = fields.Float(string='Ovs')
    ov1 = fields.Float(string='Ov1')
    ovh = fields.Float(string='Ovh')
    prs = fields.Float(string='Prs')
    upl = fields.Float(string='Upl')    
    abd = fields.Float(string='Abd')
    aul = fields.Float(string='Aul')
    sna = fields.Float(string='Sna')
    uph = fields.Float(string='Uph')
    total = fields.Float(string='Total')
    

# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AttendanceSheet(models.Model):
    _inherit = 'attendance.sheet'

    def print(self):
        
        if not self.employee_id:
            raise ValidationError(_('Please select an employee.'))
        if not self.date_from:
            raise ValidationError(_('Please select a date from.'))
        if not self.date_to:
            raise ValidationError(_('Please select a date to.'))
        
        
        action_report = self.env.ref('attendance_report.action_report_hr_daily_attendance').report_action(self)
        
        return action_report

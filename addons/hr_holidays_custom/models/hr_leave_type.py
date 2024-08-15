# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HolidaysType(models.Model):
    _inherit = "hr.leave.type"
    _description = "Leave Type"

    only_hr_validation = fields.Boolean(string='Needs only HR Validation',
        help="When selected, the Leave Requests for this type validated only by HR.")
    allocation_type = fields.Selection([
        ('fixed', 'Fixed by HR'),
        ('no', 'No allocation'),
        ('counter','Legal Leave Counter')],
        default='fixed', string='Mode',
        help='\tFixed by HR: allocated by HR and cannot be bypassed; users can request leaves;'
             '\tNo allocation: no allocation by default, users can freely request leaves;')
    unpaid = fields.Selection([('paid','Paid'),('unpaid','Unpaid'),('custom','Custom')], string='Salary Setting')
    salary_setting_ids = fields.One2many('hr.leave.salary.setting','leave_type_id', string="Custom Salary Settings")
    gm_ceo_approval = fields.Boolean("GM / CEO Approval")



class SalarySettings(models.Model):
    _name = "hr.leave.salary.setting"
    _description = "Custom Leave Salary Setting"

    days_from = fields.Integer(string="Days From")
    days_to = fields.Integer(string="Days To")
    pay_rate = fields.Float(string="Payment Rate")
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")

# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.float_utils import float_round
from datetime import datetime
from dateutil import relativedelta

class Employee(models.Model):
    _inherit = "hr.employee"

    current_leave_state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Waiting for Approve'),
        ('validate1', 'Direct Manager Approval'),
        ('validate', 'Director Approval'),
        ('approve','HR Coordinator Approval'),
        ('approve1','HR Supervisor Approval'),
        ('approve2','HR Manager Approval'),
        ('done','GM / CEO Approval'),
        ('refuse', 'Refused')])

    sick_leaves_count = fields.Float('Current Sick Leaves Counter', compute='_compute_sick_leaves')

    #@api.multi
    def _compute_sick_leaves(self):
        for record in self:
            leaves= self.env['hr.leave'].search([('employee_id','=',self.id),('holiday_status_id.only_hr_validation','=',True),('state','=','done')],order='request_date_from')
            #print ("----------------",leaves)
            days=0
            prev = leaves and leaves[0] or None
            print("leaves",leaves)
            for leave in leaves:
                print('leave',leave.request_date_from)
                if leave.request_date_from == prev.request_date_to+relativedelta.relativedelta(days=1):
                    print("if",prev.request_date_to+relativedelta.relativedelta(days=1))
                    days+=leave.number_of_days
                else:
                    print('else',prev.request_date_to+relativedelta.relativedelta(days=1),'=======',leave.request_date_from)
                    days=leave.number_of_days
                prev = leave
            record.sick_leaves_count = days

    #@api.multi
    def _compute_remaining_leaves(self):
        #remaining = self._get_remaining_leaves()
        for employee in self:
            contracts = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('state', 'in', ['open', 'pending'])])
            #print ('-----------------',contract_ids)
            leave_ids = self.env['hr.leave'].search([('employee_id','=',employee.id),('state','=','done'),('holiday_status_id.allocation_type','=','counter')])
            taken_leaves=0
            for leave in leave_ids:
                taken_leaves+=leave.number_of_days
            #print ("leaaaaaaaaaaaaaaaaaave",taken_leaves)
            if contracts:
                first_date=contracts[0].date_start
                # first_contract=contract_ids[0]
                # for contract in contract_ids:
                #     if contract.date_start < first_date:
                #         first_date=contract.date_start
                #         first_contract=contract
                current_date = datetime.now().date()
                #print("==========", first_date, '===', first_contract, '====', first_contract.date_start,"----------",current_date)
                diff_date = relativedelta.relativedelta(current_date, first_date)
                if diff_date.years >= 1:
                    leave_per_day = contracts[0].legal_leave_days/365
                    days = diff_date.years * 365+diff_date.months*30+diff_date.days
                    #print("---------------",test,'-----------',diff_date)
                    #print("------------",2019%4,"-------",2024%4)
                    # ADD one day if year % 4 == 0 and if february in the diff date
                    employee.remaining_leaves = round(days*leave_per_day,2) - taken_leaves
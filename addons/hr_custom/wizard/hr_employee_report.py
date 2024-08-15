# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo import api, fields, models


class EmployeeReport(models.TransientModel):

    _name = 'hr.employee.report'
    _description = 'Employees Report'

    report_id = fields.Many2one('hr.employee.report.setting',string="Reprot")

    #@api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['emp'] = self.env.context.get('active_ids', [])
        employees = self.env['hr.employee'].browse(data['emp'])
        datas = {
            'ids': [],
            'model': 'hr.employee',
            'form': data
        }
        return self.env.ref('hr_custom.action_report_employee').report_action(employees, data=datas)
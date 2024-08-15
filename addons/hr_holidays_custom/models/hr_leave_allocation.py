# -*- coding: utf-8 -*-

from odoo import fields, models,api
from odoo.exceptions import AccessError, UserError
from odoo.tools.translate import _

class HolidaysAllocation(models.Model):
    """ Allocation Requests Access specifications: similar to leave requests """
    _inherit = "hr.leave.allocation"
    _description = "Leaves Allocation"

    # def _default_holiday_status_id(self):
    #     if self.user_has_groups('hr_holidays.group_hr_holidays_user'):
    #         domain = [('valid', '=', True)]
    #     else:
    #         domain = [('valid', '=', True), ('allocation_type', 'in', ('no', 'fixed_allocation'))]
    #     return self.env['hr.leave.type'].search(domain, limit=1)

    name = fields.Char('Description')
    # holiday_status_id = fields.Many2one(
    #     "hr.leave.type", string="Leave Type", required=True, readonly=True,
    #     states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
    #     domain=[('valid', '=', True),('allocation_type','=','fixed')], default=_default_holiday_status_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        # ('confirm', 'HR Coordinator Confirmation'),
        ('confirm', 'HR Officer Confirmation'),
        ('refuse', 'Refused'),
        ('validate1', 'HR Supervisor Confirmation'),
        ('validate', 'HR Manager Approval')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")

    def activity_update(self):
        to_clean, to_do = self.env['hr.leave.allocation'], self.env['hr.leave.allocation']
        for allocation in self:
            if allocation.state == 'draft':
                to_clean |= allocation
            # elif allocation.state == 'confirm':
                # allocation.activity_schedule(
                #     'hr_holidays.mail_act_leave_allocation_approval',
                #     user_id=allocation.sudo()._get_responsible_for_approval().id)
            # elif allocation.state == 'validate1':
            #     allocation.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval'])
            #     allocation.activity_schedule(
            #         'hr_holidays.mail_act_leave_allocation_second_approval',
            #         user_id=allocation.sudo()._get_responsible_for_approval().id)
            elif allocation.state == 'validate':
                to_do |= allocation
            elif allocation.state == 'refuse':
                to_clean |= allocation
        if to_clean:
            to_clean.activity_unlink(['hr_holidays.mail_act_leave_allocation_approval', 'hr_holidays.mail_act_leave_allocation_second_approval'])
        if to_do:
            to_do.activity_feedback(['hr_holidays.mail_act_leave_allocation_approval', 'hr_holidays.mail_act_leave_allocation_second_approval'])

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_supervisor = self.env.user.has_group('hr_custom.group_hr_supervisor')
        is_manager = self.env.user.has_group('hr_custom.group_hr_manager')
        is_it_manager = self.env.user.has_group('hr_custom.group_it_hr_manager')
        for holiday in self:
            # val_type = holiday.holiday_status_id.validation_type
            if holiday.state  in ['validate','validate1'] and not is_supervisor and not is_manager and not is_it_manager:
                raise UserError(_('Only HR Supervisor or HR Manager can approve or refuse allocation requests.'))

            # if state == 'validate1' and not is_manager:
            #     raise UserError(_('Only HR Manager can approve or refuse allocation requests.'))

            # if state == 'draft':
            #     if holiday.employee_id != current_employee and not is_manager:
            #         raise UserError(_('Only a Leave Manager can reset other people leaves.'))
            #     continue
            #
            # if not is_officer:
            #     raise UserError(_('Only HR Supervisor or HR Manager can approve or refuse allocation requests.'))

            # if is_officer:
            #     # use ir.rule based first access check: department, members, ... (see security.xml)
            #     holiday.check_access_rule('write')
            #
            # if holiday.employee_id == current_employee and not is_manager:
            #     raise UserError(_('Only a Leave Manager can approve its own requests.'))
            #
            # if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
            #     manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
            #     if (manager and manager != current_employee) and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (holiday.employee_id.name))
            #
            # if state == 'validate' and val_type == 'both':
            #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            #         raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))
# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools import float_compare

class HolidaysRequest(models.Model):
    _inherit = "hr.leave"
    _description = "Leave"

    state = fields.Selection([
        # ('draft', 'draft'),
        # ('cancel', 'Cancelled'),
        # ('confirm', 'Direct Manager Approval'),
        # ('refuse', 'Refused'),
        # ('validate1', ' '),
        # ('validate', 'Director Approval'),
        # ('validate2', 'HR Coordinator Validation'),
        # ('validate3', 'HR Supervisor Validation'),
        # ('done', 'HR Manager Validation'),
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Waiting for Approve'),
        ('validate1', 'Direct Manager Approval'),
        ('validate', 'Director Approval'),
        ('approve','HR Coordinator Approval'),
        ('approve1','HR Supervisor Approval'),
        ('approve2','HR Manager Approval'),
        ('done','GM / CEO Approval'),
        ('refuse', 'Refused'),
  ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")

    approval_user = fields.Boolean(compute="_get_approval_user",string="Approval User")
    check_ceo_approval = fields.Boolean(related='holiday_status_id.gm_ceo_approval')
    substitute_employee = fields.Many2one('hr.employee', string="Substitute Employee")


    def _get_approval_user(self):
        parent= self.sudo().search([('id','=',self.id),('employee_id.parent_id.user_id','=',self.env.user.id)])
        parent_parent= self.sudo().search([('id','=',self.id),('employee_id.parent_id.parent_id.user_id','=',self.env.user.id)])
        if self.state == 'confirm' and parent:
            self.approval_user =True
        # elif self.state == 'validate1':
        #     if not(self.employee_id.company_id.parent_id) and not(self.employee_id.company_id.child_ids) and self.env.user.has_group('hr_custom.group_it_hr_manager'):
        #         self.approval_user = True
        #     elif (self.employee_id.company_id.parent_id or self.employee_id.company_id.child_ids) and parent_parent:
        #         self.approval_user = True
        #     elif (self.employee_id.company_id.parent_id or self.employee_id.company_id.child_ids) and not(self.employee_id.parent_id.parent_id) and parent:
        #         self.approval_user = True
        elif self.state == 'validate1' and parent_parent:
            self.approval_user = True
        # elif self.state == 'validate' and self.env.user.has_group('hr_custom.group_hr_coordinator'):
        #     self.approval_user = True
        # elif self.state == 'approve' and self.env.user.has_group('hr_custom.group_hr_supervisor'):
        #     self.approval_user = True
        # elif self.state == 'approve1' and self.env.user.has_group('hr_custom.group_hr_manager'):
        #     self.approval_user = True
        else:
            self.approval_user = False

    # #@api.multi
    # def dm_approve(self):
    #     # if self.filtered(lambda holiday: holiday.state != 'draft'):
    #     #     raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
    #     # if self.holiday_status_id.only_hr_validation == True:
    #     #     self.write({'state': 'validate'})
    #     # else:
    #     #     self.write({'state': 'confirm'})
    #     # self.activity_update()
    #     self.write({'state': 'confirm'})
    #     return True

    #@api.multi
    def action_confirm(self):
        #  print ('confirmed',self.employee_id.name)
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        # if self.holiday_status_id.only_hr_validation == True:
        #     self.write({'state': 'validate'})
        # else:
        #     self.write({'state': 'confirm'})
        self.write({'state': 'confirm'})
        self.activity_update()
        #print(self.state)
        return True

    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        # employee_id = values.get('employee_id', False)
        # if not values.get('department_id'):
        #     values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})

        holiday = super(HolidaysRequest, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
        if holiday.holiday_status_id.only_hr_validation:
            holiday.write({'state':'draft'})
            holiday.action_confirm()
            holiday._compute_can_approve()
            holiday.action_validate()
            #print ('validation------------',self.state)
        # if not self._context.get('leave_fast_create'):
        #     holiday.add_follower(employee_id)
        #     if 'employee_id' in values:
        #         holiday._onchange_employee_id()
        #     if not self._context.get('import_file'):
        #         holiday.activity_update()
        return holiday

    #@api.multi
    def action_approve1(self):
        if self.filtered(lambda holiday: holiday.state != 'validate'):
            raise UserError(_('Leave request must be in Approved state in order to validate it.'))
        self.write({'state': 'approve'})
        self.activity_update()
        return True

    #@api.multi
    def action_approve2(self):
        if self.filtered(lambda holiday: holiday.state != 'approve'):
            raise UserError(_('Leave request must be in Validated state in order to second validate it.'))
        self.write({'state': 'approve1'})
        self.activity_update()
        return True

    #@api.multi
    def action_done(self):
        if self.filtered(lambda holiday: holiday.state != 'approve1'):
            raise UserError(_('Leave request must be in Approved state in order to approve it.'))
        self.write({'state': 'done'})
        self.activity_update()
        return True
    ###################### IT CODE ################################
    # #@api.multi
    # def it_action_done(self):
    #     if self.filtered(lambda holiday: holiday.state not in  ['validate','validate1']):
    #         raise UserError(_('Leave request must be in Approved by direct manager state in order to approve it.'))
    #     self.write({'state': 'approve2'})
    #     self.activity_update()
    #     return True
    #
    #@api.multi
    def action_approve3(self):
        if self.filtered(lambda holiday: holiday.state not in  ['validate','validate1']):
            raise UserError(_('Leave request must be in Approved by direct manager state in order to approve it.'))
        self.write({'state': 'approve2'})
        self.activity_update()
        return True

    #@api.multi
    def action_approve4(self):
        if self.filtered(lambda holiday: holiday.state not in  ['validate','validate1','approve2']):
            raise UserError(_('Leave request must be in Approved by direct manager state in order to approve it.'))
        self.write({'state': 'done'})
        self.activity_update()
        return True
    #################### END OF IT CODE ###########################
    #@api.multi
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1','approve2','approve','approve1','done']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'first_approver_id': current_employee.id})
            else:
                holiday.write({'state': 'refuse', 'second_approver_id': current_employee.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        self.activity_update()
        return True

    # #@api.multi
    # def action_approve(self):
    #     if self.env.user.id != self.employee_id.parent_id.user_id.id:
    #         raise UserError(_('Leave request must be confirmed by direct manager(%s).'%self.employee_id.parent_id.name))
    #     return super(HolidaysRequest, self).action_approve()

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        # current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        # is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        # for holiday in self:
        #     val_type = holiday.holiday_status_id.validation_type
        #     if state == 'confirm' and self.env.user.id != self.employee_id.parent_id.user_id.id:
        #         raise UserError(_('Leave request must be confirmed by direct manager(%s).' % self.employee_id.parent_id.name))
            # if state == 'validate' and self.env.user.id != self.employee_id.parent_id.parent_id.user_id.id:
            #     print ("seeeeeeeeeeeeeeeeeeeecond if")
            #     raise UserError( _('Leave request must be confirmed  manager(%s).' % self.employee_id.parent_id.parent_id.user_id.name))                # continue

            # if state == 'draft':
            #     if holiday.employee_id != current_employee and not is_manager:
            #         raise UserError(_('Only a Leave Manager can reset other people leaves.'))
            #     continue

            # if not is_officer:
            #     raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))
            #
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


    # #@api.multi
    # def action_approve(self):
    #     # if validation_type == 'both': this method is the first approval approval
    #     # if validation_type != 'both': this method calls action_validate() below
    #     if any(holiday.state != 'confirm' for holiday in self):
    #         raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))
    #
    #     current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #     self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})
    #     self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
    #     if not self.env.context.get('leave_fast_create'):
    #         self.activity_update()
    #     return True

    @api.constrains('number_of_days','employee_id','holiday_status_id')
    def _check_holidays(self):
        #print("sub----------------------------")
        #res = super( HolidaysRequest, self)._check_holidays()
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.allocation_type == 'no':
                continue
            leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
            if holiday.holiday_status_id.allocation_type != 'counter' and (float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
              float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1):
                #print ("shhhhhhhhhhhhhhhhhhhhhhhhhhhhhhit")
                raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                        'Please also check the leaves waiting for validation.'))
            if holiday.holiday_status_id.allocation_type == 'counter' and holiday.employee_id.remaining_leaves < holiday.number_of_days_display:
                #print ("sub----------------------------",holiday.employee_id.remaining_leaves,'----',holiday.number_of_days_display)
                raise ValidationError(_('The number of remaining leaves is not sufficient for %s.'%holiday.employee_id.name))

class TestWizard(models.TransientModel):

    _name = 'test.wizard'
    _description = 'HR Leaves Summary Report By Department'

    name = fields.Char(string="Name")

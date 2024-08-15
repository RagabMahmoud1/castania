# -*- coding: utf-8 -*-

from odoo import models, fields, api , exceptions


class hr_custody_type(models.Model):
    _name = 'hr.custody.type'
    _description = "Custody Type"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Name", required=True)
    total_no = fields.Integer('Total No')
    available_no = fields.Integer(string="Available No", readonly=True, compute="compute_available", track_visibility='onchange')
    taken_no = fields.Integer(string="Taken No", readonly=True, compute="compute_taken", track_visibility='onchange')
    custody_ids = fields.One2many('hr.custody', 'custody_type_id', string="Employees")
    note = fields.Text("Notes")


    #@api.multi
    @api.depends('total_no', 'taken_no')
    def compute_available(self):
        for record in self:
            var = 0.0
            var = record.total_no - record.taken_no
            record.available_no = var
            #print("yeeeeeeeeeeeeeeeeeeeeeeeees")

    #@api.multi
    def compute_taken(self):
        for record in self:
            #custody_type = self.env['hr.custody'].search([('custody_type_id', '=', record.id)])
            #print("6666666666666666666", custody_type)
            for custody in record.custody_ids:
                if custody.state == 'deliver':
                    record.taken_no +=1
                #print("########")



# class hr_employee_custody(models.Model):
#     _name = 'hr.employee.custody'
#
#     name = fields.Many2one('hr.employee', string="Employee", required=True)
#     custody_ids = fields.One2many('hr.custody', 'employee_custody_id', string="Custody", required=True, readonly=False)


class hr_custody(models.Model):
    _name = 'hr.custody'
    _description = "Custody"

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    receive_date = fields.Date(string="Receive Date")
    delivery_date = fields.Date(string="Delivery Date")
    state = fields.Selection([("draft", "Draft"),
                              ("deliver", "Delivered to Employee"),
                              ("receive", "Received from Employee")], default='draft', readonly=True)
    custody_type_id = fields.Many2one('hr.custody.type', string="Custody")



    #@api.multi
    def set_to_draft(self):
        for record in self:
            if record.state == 'deliver':
                record.state = 'draft'

    #@api.multi
    def delivered(self):
        for record in self:
            if not record.delivery_date:
                raise exceptions.ValidationError("Insert Delivery Date")
            if record.custody_type_id.available_no <= 0:
                raise exceptions.ValidationError("This Custody is not Available")
            else:
                record.state = 'deliver'

    #@api.multi
    def received(self):
        for record in self:
            if not record.receive_date:
                raise exceptions.ValidationError("Insert Receive Date")
            else:
                record.state = 'receive'


class Employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    custody_ids = fields.One2many('hr.custody', 'employee_id')

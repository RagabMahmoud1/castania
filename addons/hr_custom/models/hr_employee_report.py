# -*- coding: utf-8 -*-

from odoo import models, fields, api , exceptions


class HrEmoloyeeReportSetting(models.Model):
    _name = 'hr.employee.report.setting'
    _description = "Employee Report Setting"

    name = fields.Char(string="Report Name", required=True)
    column_ids = fields.One2many('hr.employee.report.column','report_id', string="Columns")
    company_id = fields.Many2one('res.company', string='Company')
    # emp_no = fields.Boolean(string="Employee No")
    # name = fields.Boolean(string="Name")
    # #address_home_id = fields.Many2one
    # country_id = fields.Boolean(string='Nationality (Country)')
    # gender = fields.Boolean(string="Gender")
    # marital = fields.Boolean(string='Marital Status')
    # children = fields.Boolean(string='Number of Children')
    # place_of_birth = fields.Boolean(string='Place of Birth')
    # country_of_birth = fields.Boolean(string="Country of Birth")
    # birthday = fields.Boolean(string='Date of Birth')
    # ssnid = fields.Boolean(string='SSN No')
    # sinid = fields.Boolean(string='SIN No')
    # identification_id = fields.Boolean(string='Identification No')

class HrEmoloyeeReportColumn(models.Model):
    _name = 'hr.employee.report.column'
    _description = "Employee Report Column"

    def _get_fields(self):
        fields = self.env['ir.model'].search([('model','=','hr.employee')])[0].field_id
        return [(x.name, x.field_description) for x in fields if x.name not in ['__last_update','create_date','create_uid','display_name','id','write_date','write_uid','appraisal_employee'] and x.ttype not in ['many2many','one2many','binary'] ]

    sequence = fields.Integer("Sequence", readonly=True, compute='incs', store=True)
    field = fields.Selection(selection=_get_fields, string="Field")
    report_id = fields.Many2one('hr.employee.report.setting', string="Report")

    #generate the field sequence
    #@api.one
    @api.depends('report_id')
    def incs(self):
        if self.id:
            get_previous_id = self.search(
                [ ('report_id', '=', self.report_id.id)])
            seq_list =  list(get_previous_id)
            for seq in seq_list :
                if seq.id ==  self.id :
                    self.sequence = seq_list.index(seq)+1

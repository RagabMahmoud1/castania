#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError

class EmployeeReport(models.AbstractModel):
    _name = 'report.hr_custom.report_employee'
    _description = 'Employees Report'

    # def get_header_old(self,form):
    #     model_id = self.env['ir.model'].search([('model', '=', 'hr.employee.report.setting')])
    #     fields=[]
    #     if model_id:
    #         for field in model_id.field_id:
    #             if field.name not in ['__last_update','create_date','create_uid','display_name','id','write_date','write_uid']:
    #                 check=None
    #                 check = self.env['hr.employee.report.setting'].search([(field.name,'=','True'),('id','=',form['report_id'][0])])
    #                 if check:
    #                     fields.append((field.name,field.field_description))
    #         return fields
    def get_header(self,form):
        fields = []
        model_id = self.env['ir.model'].search([('model', '=', 'hr.employee')])
        for column in self.env['hr.employee.report.setting'].browse(form['report_id'][0]).column_ids:
            print('1---------------',model_id.id)
            field = self.env['ir.model.fields'].search([('name', '=',column.field),('model_id','=',model_id.id)])
            print ('333333333',field)
            fields.append((field.name,field.field_description))
            print(field.field_description)
        return fields

    def get_body(self,form,employees):
        header = self.get_header(form)
        result=[]
        for employee in employees:
            record=[]
            for field in header:
                value = employee.read(field)
                print(value)
                if value:
                    record.append(value[0][field[0]])
                else:
                    record.append('')
            result.append(record)
        return result

    #@api.multi
    def _get_report_values(self, docids, data=None):
        print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",data)
        employees = self.env['hr.employee'].browse(data['context']['active_ids'])
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'data': data,
            'header': self.get_header(data['form']),
            'body': self.get_body(data['form'],employees),
            # 'get_slip': self.get_slip,
            # 'get_values': self.get_values,
            # 'get_employee': self.get_employee,
            # 'get_total': self.get_total,

        }

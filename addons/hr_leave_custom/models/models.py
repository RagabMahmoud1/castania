# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class hr_leave_custom(models.Model):
#     _name = 'hr_leave_custom.hr_leave_custom'
#     _description = 'hr_leave_custom.hr_leave_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


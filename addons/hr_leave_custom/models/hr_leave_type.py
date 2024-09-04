# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    holiday_type = fields.Selection([
        ('religious', 'Religious'),
        ('company', 'Company'),
        ('national', 'National'),
        ('others', 'Others'),
        ('special', 'Special'),
    ], string='Holiday Type', default=False)    
    fixed = fields.Boolean(string='Fixed', default=False)
    presence_type = fields.Text(string='Duty on/ Duty off Presence Type', default=False)
        
    presence_type_id = fields.Selection([
        ('upl', 'UPL'),
        ('abd', 'ABD'),
        ('aul', 'AUL'),
        ('sna', 'SNA'),
        ('uph', 'UPH'),
    ], string='Presence Type', default=False)
    
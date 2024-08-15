# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    holiday_type = fields.Selection([
        ('religious', 'Religious'),
        ('company', 'Company'),
        ('national', 'National'),
        ('others', 'Others'),
        ('special', 'Special'),
    ], string='Holiday Type', default=False)    
    fixed = fields.Boolean(string='Fixed', default=False)
    presence_type = fields.Text(string='Duty on/ Duty off Presence Type', default=False)
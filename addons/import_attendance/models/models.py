from odoo import models, fields, api
from datetime import datetime
import base64

class ImportAttendance(models.TransientModel):
    _name = 'import.attendance'

    file = fields.Binary(string='File', required=True)
    filename = fields.Char(string='Filename')

    def import_file(self):
        if self.file:
            file_content = base64.b64decode(self.file).decode('utf-8')
            lines = file_content.strip().split('\n')
            data_list = []

            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    timestamp_str = parts[1] + ' ' + parts[2]
                    in_out = int(parts[3])
                    data_list.append({
                        'x_studio_id': parts[0],
                        'timestamp': timestamp_str,
                        'in_out': in_out,
                    })

            sorted_data_list = sorted(data_list, key=lambda x: datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M:%S'))

            for data in sorted_data_list:
                employee_id = self.env['hr.employee'].sudo().search([('x_studio_id', '=', data['x_studio_id'])])
                if not employee_id:
                    continue

                existing_attendance = self.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', employee_id.id),
                    ('check_in', '=', data['timestamp']),
                ])
                if existing_attendance:
                    continue

                if data['in_out'] == 0:
                    self.env['hr.attendance'].sudo().create({
                        'employee_id': employee_id.id,
                        'check_in': data['timestamp'],
                    })
                elif data['in_out'] == 1:
                    last_attendance = self.env['hr.attendance'].sudo().search([
                        ('employee_id', '=', employee_id.id),
                        ('check_in', '<=', data['timestamp']),
                        ('check_out', '=', False),
                    ], order='check_in desc', limit=1)
                    if last_attendance:
                        last_attendance.write({'check_out': data['timestamp']})
                    else:
                        self.env['hr.attendance'].sudo().create({
                            'employee_id': employee_id.id,
                            'check_in': data['timestamp'],
                            'check_out': data['timestamp'],
                        })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _same_date(self, date_1, date_2):
        timestamp1 = date_1
        timestamp2 = datetime.strptime(date_2, '%Y-%m-%d %H:%M:%S')
        return timestamp1.date() == timestamp2.date()


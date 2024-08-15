# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models
from datetime import date, timedelta, datetime



_logger = logging.getLogger(__name__)

class Contract(models.Model):

    _name = 'hr.contract'
    _inherit = ['hr.contract','mail.thread','mail.activity.mixin']
    _mail_post_access='read'
    _description = 'Contract'
    # _mail_post_access = 'read'

    # bonus = fields.Monetary(string='Bonus', digits=(16, 2), help="Employee's monthly Bonus.")
    legal_leave_days = fields.Integer(string="Legal Leave Days")
    # bonus_structure_id = fields.Many2one('hr.payroll.structure', string="Bonus Structure")
    # total_salary = fields.Monetary('Total Salary', digits=(16, 2), track_visibility="onchange")
    # presidential_incentive = fields.Float(string="Presidential Incentive")
    # CEO_incentive = fields.Float(string="CEO Incentive")
    # fuel_incentive = fields.Float(string="Fuel Incentive")
    # phone_incentive = fields.Float(string="Phone Incentive")
    # miles_incentive = fields.Float(string="Car Miles Incentive")
    # wage = fields.Monetary('Wage', digits=(16, 2),  track_visibility="onchange", help="Employee's monthly gross wage.")
    date_end_alarm = fields.Date('End Date Alarm',track_visibility="onchange",dafaule= lambda self:self.date_end)
    user_id = fields.Many2one('res.users', "Responsible", track_visibility="onchange", default=lambda self: self.env.uid)
    # new_incentive = fields.Float(string="New Incentive")
    # wage_percentage = fields.Float(string='Wage Percentage')
    # bonus_percentage = fields.Float(string='Bonus Percentage')
    # bonus_structure_id = fields.Many2one('hr.payroll.structure', string="Bonus Structure")
    # struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')

    # #@api.multi
    # @api.depends('total_salary')
    # @api.onchange('total_salary')
    # def compute_amounts(self):
    #     # config = self.env['res.config.settings'].get_values()
    #     #print(config)
    #     for record in self:
    #         # if config:
    #             # record.presidential_incentive = config['presidential_incentive']
    #         record.wage = (record.total_salary*self.wage_percentage/100) + record.presidential_incentive + record.new_incentive
    #         record.bonus = (record.total_salary * self.bonus_percentage / 100) - record.presidential_incentive - record.new_incentive + record.

    @api.model
    # #@api.multi
    @api.depends('date_end_alarm')
    # @api.onchange('date_end_alarm')
    def send_notification(self):
        contract=self.search([])
        for record in contract:
            current_date = date.today()
            alarm=record.date_end_alarm
            if current_date==alarm:
                contract_name = contract.name
                message_env = self.env['mail.channel']
                # user = self.env['res.partner'].sudo().browse(record.employee_id.user_id.partner_id.id)
                user= record.user_id
                admin = self.env['res.users'].browse(2).partner_id  # partners_to = [user]
                partners_to = [user.partner_id.id, admin.id]
                employee = record.employee_id.name
                end_date = str(record.date_end)
                body = '<h5 style="color:#888">' + 'Contract Notification <b> ' '</h5>' + 'The contract : <b> ' + contract_name + ' </b>' + 'of the employee <b>' + employee + ' </b>' + ' </b> end date in <b >' + \
                       ' </b>' + end_date + '</b>'
                message_env.env.cr.execute("""
                                                    SELECT P.channel_id as channel_id
                                                    FROM mail_channel C, mail_channel_partner P
                                                    WHERE P.channel_id = C.id
                                                        AND C.public LIKE 'private'
                                                        AND P.partner_id IN %s
                                                        AND channel_type LIKE 'chat'
                                                    GROUP BY P.channel_id
                                                    HAVING array_agg(P.partner_id ORDER BY P.partner_id) = %s
                                                """, (tuple(partners_to), sorted(list(partners_to)),))
                result = message_env.env.cr.dictfetchall()
                if result:
                    channel = message_env.browse(result[0].get('channel_id'))
                    channel.message_post(body=body, subtype='mail.mt_comment', author_id=admin.id)

                    print(channel.name, result)

                else:
                    channel = message_env.create({
                        'public': 'private',
                        'channel_type': 'chat',
                        'email_send': False,
                        'name': ', '.join(
                            self.env['res.partner'].sudo().browse(user.partner_id.id).mapped('name')),
                        'channel_last_seen_partner_ids': [
                            (0, 0, {
                                'partner_id': user.partner_id.id,
                                'channel_id': self.id
                            }),
                            (0, 0, {
                                'partner_id': admin.id,
                                'channel_id': self.id
                            }),
                        ]
                    })

                    channel.message_post(body=body, subtype='mail.mt_comment', author_id=admin.id)









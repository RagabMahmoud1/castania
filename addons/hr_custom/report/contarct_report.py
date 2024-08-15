import num2words
import random
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime


class ContractReport(models.Model):
    _inherit = 'hr.contract'
    _description = 'Contract Report'

    day_contract = fields.Char('Today', compute="compute_day")
    # fields for convert wage and bonus to arabic
    new_wage = fields.Char('New Wage', compute="compute_method_salary_arabic")
    new_bonus = fields.Char('New bonus', compute="compute_method_bonus_arabic")

    # fields from calculate the salary
    total_salary = fields.Monetary('total salary')
    basic_salary = fields.Float(string="Basic Salary", compute="calculate_salary_rule")
    cola = fields.Float(string="cola", compute="calculate_salary_rule")
    accommodation_allowance = fields.Float(string="Accommodation Allowance", compute="calculate_salary_rule")
    car_miles_incentive = fields.Float(string="Car Miles Incentive", compute="calculate_salary_rule")
    presidential_incentive = fields.Float(string="Presidential Incentive", compute="calculate_salary_rule")
    total = fields.Float(string="Total", compute="calculate_salary_rule")

    # fields from calculate bonus
    bonus = fields.Monetary(string='bonus')
    bonus_incentive = fields.Float(string='Bonus Incentive', compute="calculate_bonus_rule")
    managerial_incentive = fields.Float(string='Managerial Incentive', compute="calculate_bonus_rule")
    overtime_incentive = fields.Float(string='Overtime Incentive', compute="calculate_bonus_rule")
    meal_incentive = fields.Float(string='Meal Incentive', compute="calculate_bonus_rule")
    work_nature_incentive = fields.Float(string='Work Nature Incentive', compute="calculate_bonus_rule")
    treatment_incentive = fields.Float(string='Treatment Incentive', compute="calculate_bonus_rule")
    ceo_incentive = fields.Float(string='CEO incentive', compute="calculate_bonus_rule")
    total_bonus = fields.Float(string='Bonus Total', compute="calculate_bonus_rule")

    # function for extract date
    @api.depends('date_start')
    def compute_day(self):

        convert_date = datetime.strftime(self.date_start, "%A")
        self.day_contract = convert_date




    # function for convert number to arabic string
    @api.depends('total_salary')
    def compute_method_salary_arabic(self):
        self.new_wage = str(num2words.num2words(self.total_salary, lang='ar_SY'))

    @api.depends('bonus')
    def compute_method_bonus_arabic(self):
        self.new_bonus = str(num2words.num2words(self.bonus, lang='ar_SY'))

    # function for salary rule
    @api.depends('total_salary')
    def calculate_salary_rule(self):
        for struct in self.struct_id:
            rules = struct.env['hr.salary.rule'].search([])
            for rule in rules:
                if rule.code == "BASIC":
                    self.basic_salary = self.total_salary * rule.amount_percentage / 100.0

                elif rule.code == "COLA":
                    self.cola = self.total_salary * rule.amount_percentage / 100.0

                elif rule.code == "ACC1":
                    self.accommodation_allowance = self.total_salary * rule.amount_percentage / 100.0

                elif rule.code == "CMINC":
                    self.car_miles_incentive = self.miles_incentive

                elif rule.code == "PRSINC":
                    self.presidential_incentive = self.presidential_incentive

            self.total = self.basic_salary + self.cola + self.accommodation_allowance + self.car_miles_incentive + self.presidential_incentive

    # function for bonus in salary

    @api.depends('bonus')
    def calculate_bonus_rule(self):
        for rec in self.bonus_structure_id:
            rules = rec.env['hr.salary.rule'].search([])
            for rule in rules:
                if rule.code == "MGRINC":
                    self.managerial_incentive = self.bonus * rule.amount_percentage / 100.0

                elif rule.code == "BONINC":
                    self.bonus_incentive = self.bonus * rule.amount_percentage / 100.0

                elif rule.code == "OVTINC":
                    self.overtime_incentive = self.bonus * rule.amount_percentage / 100.0

                elif rule.code == "MEALINC":
                    self.meal_incentive = self.bonus * rule.amount_percentage / 100.0

                elif rule.code == "WNINC":
                    self.work_nature_incentive = self.bonus * rule.amount_percentage / 100.0

                elif rule.code == "TRTINC":
                    self.treatment_incentive = self.bonus * rule.amount_percentage / 100.0

                elif rule.code == "CEOINC":
                    self.ceo_incentive = self.CEO_incentive

            self.total_bonus = self.managerial_incentive + self.bonus_incentive + self.overtime_incentive + self.meal_incentive + self.work_nature_incentive + self.treatment_incentive + self.ceo_incentive

    # for print report
    #@api.multi
    def print_form(self):
        return self.env.ref('hr_custom.action_report_contract_report').report_action(self)

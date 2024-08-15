from odoo import fields, models, api



class BankList(models.Model):
    _name = "bank.list"
    _description = "Employees Bank List"

    name = fields.Char(string='Bank Code')

class BankPartner(models.Model):
    _inherit = 'res.partner.bank'

    bank_code = fields.Many2one('bank.list', string="Bank Code")



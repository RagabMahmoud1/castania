from odoo import api, fields, models,exceptions
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta, MO



class EmployeeDegree(models.Model):
    _name = "hr.employee.degree"
    _description = "Employee Degree"
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the Degree of Recruitment must be unique!')
    ]

    name = fields.Char("Degree", required=True, translate=True)
    sequence = fields.Integer("Sequence", default=1, help="Gives the sequence order when displaying a list of degrees.")

class qualification(models.Model):
    _name = 'hr.employee.qualification'
    _description = 'Employee Qualification'

    university_id = fields.Many2one('hr.employee.university', required =True)
    graduation_date= fields.Date('Graduation Date', required =True)
    major=fields.Char('Major', required =True)
    general_grade=fields.Selection([("excellent","Excellent"),("vgood","Very Good"),("good","Good")], string='General Rate', required =True)
    degree_id= fields.Many2one('hr.employee.degree' , string="Type", required =True )
    employee_id = fields.Many2one('hr.employee', string="Employee")
    location = fields.Many2one('res.country', string="University Location")

class additional_certificate(models.Model):
    _name = 'hr.employee.add.qualification'
    _description = 'Employee Additional Certificate'

    certificate_id=fields.Many2one('hr.employee.certificate', required =True)
    earned_date= fields.Date('Earned Date', required =True)
    certificate_institution=fields.Char('Institution', required =True)
    general_grade=fields.Selection([("excellent","Excellent"),("vgood","Very Good"),("good","Good")], string='General Rate')
    employee_id = fields.Many2one('hr.employee', string="Employee")
#

class certificate(models.Model):
    _name = 'hr.employee.certificate'
    _description = 'Certificate'

    name = fields.Char('Certificate Name', required=True)



class training_courses(models.Model):
    _name = 'hr.employee.course'
    _description = 'Employee Courses'

    course_name=fields.Char('Course Name')
    start_date=fields.Date('Start Date')
    end_date = fields.Date('End Date')
    institution_name=fields.Char('Institution Name ')
    employee_id = fields.Many2one('hr.employee', string="Employee")


class Employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    qualification_ids = fields.One2many('hr.employee.qualification', 'employee_id', string="Qualification")
    certificate_additional_ids = fields.One2many('hr.employee.add.qualification', 'employee_id', string="Certificate and Additional Qualification")
    training_courses_ids = fields.One2many('hr.employee.course','employee_id', string="Training  and Courses")
    emp_no = fields.Char(string="Employee NO", copy=False)
    age = fields.Integer(compute="compute_age",string="Age")
    start_date = fields.Date(compute='_compute_start_date', string="Start Date")
    # year_num=fields.Many2one('hr.contract', string='Worked Year',compute='compute_year',readonly=True)
    service_years = fields.Integer(compute="compute_service_years",string="Service Years")
    service_months = fields.Integer(compute="compute_service_months",string="Service Months")
    service_days = fields.Integer(compute="compute_service_days",string="Service Days")
    study_school = fields.Char("University", groups="hr.group_hr_user")
    medical_category = fields.Selection([('A','A'),('B','B'),('VIP','VIP')],string='Medical insurance category')
    nationality_type = fields.Selection([('By Birth','By Birth'),('By naturalization','By naturalization')],'Type of nationality')
    mother_name = fields.Char(string="Name of Mother")
    address_home = fields.Char(string="Address")
    active = fields.Boolean('Active', default=True)

    @api.model
    def create(self, data_list):
        data_list['emp_no'] = self.env['ir.sequence'].next_by_code('hr.employee')
        return super(Employee, self).create(data_list)

    @api.onchange('birthday')
    def compute_age(self):
        if self.birthday:
            current_date = date.today()
            birthdate = datetime.strptime(str(self.birthday), "%Y-%m-%d")
            self.age = relativedelta(current_date, birthdate).years

    @api.constrains('birthday')
    def _check_birthday_not_in_future(self):
        # print('*********************************************\n')
        current_date = str(datetime.now().date())
        for r in self:
            if r.birthday and str(r.birthday) > str(current_date):
                raise exceptions.ValidationError("Birthday Can't be in FUTURE!")

    # @api.onchange('year_num')
    # def compute_year(self):
    #     if self.year_num.date_start:
    #         current_date = date.today()
    #         number_year = datetime.strptime(str(self.year_num.date_start), "%Y-%m-%d")
    #         self.count_year = relativedelta(current_date, number_year).years
    # #@api.one
    def _compute_start_date(self):
        self.ensure_one()
        contracts = self.env['hr.contract'].search([('employee_id','=',self.id),('state','in',['open','pending'])])
        if contracts:
            first_date =contracts[0].date_start
            # for contract in contracts:
            #     if contract.date_start < first_date:
            #         first_date = contract.date_start
            self.start_date = first_date

    def compute_service_years(self):
        if self.start_date:
            current_date = date.today()
            start_date = datetime.strptime(str(self.start_date), "%Y-%m-%d")
            self.service_years = relativedelta(current_date, start_date).years

    def compute_service_months(self):
        if self.start_date:
            current_date = date.today()
            start_date = datetime.strptime(str(self.start_date), "%Y-%m-%d")
            self.service_months = relativedelta(current_date, start_date).months

    def compute_service_days(self):
        if self.start_date:
            current_date = date.today()
            start_date = datetime.strptime(str(self.start_date), "%Y-%m-%d")
            self.service_days = relativedelta(current_date, start_date).days

class hr_university(models.Model):
    _name = 'hr.employee.university'
    _description = "Employee University"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code',)

class Department(models.Model):
    _inherit = "hr.department"
    _description = "HR Department"
    # _inherit = ['mail.thread']
    # _order = "name"
    _rec_name = 'name'

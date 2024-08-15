# -*- coding: utf-8 -*-

{
    'name': 'HR Custom',
    'sequence': 1,
    'category': 'Human Resources',
    'version': '17.0',
    'author': "GSK-IT",
    'website': "http://www.gsk-sd.com",
    'description': "Additional features for HR module",

    'depends': [
        'base','hr','hr_contract','mail', 'hr_appraisal'
    ],
    'data': [
	'views/template.xml',
        'security/hr_custom_security.xml',
        'views/hr_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_custody_views.xml',
        'views/hr_custom_report.xml',
        'views/hr_employee_report_views.xml',    
        'report/hr_employee_report_templates.xml',
        'report/contarct_report.xml',
        'report/contarct_report_templete.xml',
        'wizard/hr_employee_report.xml',
        'data/hr_data.xml',
        'data/hr_employee_sequence.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    
}

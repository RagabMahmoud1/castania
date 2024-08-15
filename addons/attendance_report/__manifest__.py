# -*- coding: utf-8 -*-
{
    'name': "attendance report",

    'summary': "attendance report",

    'description': """
attendance report
    """,

    'author': "Ragab",
    'website': "",

    'category': 'HR',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance', 'hr_holidays', 'hr_holidays_attendance', 'hr_contract', 'hr_payroll'],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "wizard/hr_attendance_report_wizard.xml",
        "report/hr_daily_attendance_report_report.xml"
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}


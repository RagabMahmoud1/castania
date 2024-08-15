# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Sheet And Policies",

    'summary': """Managing  Attendance Sheets for Employees
        """,
    'description': """
        Employees Attendance Sheet Management   
    """,
    'author': "Ramadan Khalil",
    'website': "rkhalil1990@gmail.com",
    'category': 'hr',
    'version': '13.001',
    'images': ['static/description/bannar.jpg'],

    'depends': ['base',
                'hr',
                'hr_payroll',
                'hr_holidays',
                'hr_attendance'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/change_att_data_view.xml',
        'wizard/employee_attendance_view.xml',
        'wizard/attendance_view.xml',
        'views/hr_attendance_sheet_view.xml',
        'views/hr_attendance_policy_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_public_holiday_view.xml',
        'views/hr_attendance.xml',
        'reports/employee_attendance_report.xml',
        'reports/attendance_report.xml',
        'data/data.xml',

    ],

    'license': 'LGPL-3',

    # 'demo': [
    #     'demo/demo.xml',
    # ],
}

# -*- coding: utf-8 -*-
{
    'name': "Hr Attendance Sheet Extra",

    'summary': """
        """,

    'description': """
    """,

    'author': "Eng.Ramadan Khalil",
    'website': "",
    'license': 'LGPL-3',
    'category': 'hr',
    'version': '13.0.0',

    'depends': ['base','hr_attendance_sheet'],

    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/att_sheet_batch_view.xml',
        'views/attendance_sheet_view.xml',
        'data/mail_template.xml',

    ],

}
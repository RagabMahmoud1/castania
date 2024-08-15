# -*- coding: utf-8 -*-

{
    'name': 'HR Custom Leave',
    'sequence': 3,
    'category': 'Human Resources',
    'version': '17.0',
    'author': "GSK-IT",
    'website': "http://www.gsk-sd.com",
    'description': "Additional features for Holiday module",

    'depends': [
        'hr_holidays','hr_custom'
    ],
    'data': [
	    # 'views/template.xml',
        'views/hr_leave_views.xml',
        'views/hr_leave_allocation_views.xml',
        'views/hr_leave_type_view.xml',
        'views/hr_views.xml',
        'data/hr_holidays_data.xml',
        'security/ir.model.access.csv',
        'security/hr_holidays_security.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    
}

{
    'name': 'National ID Registration Module',
    'version': '1.1',
    'category': 'Registration',
    'summary': 'Online National ID Application Processing with SMS/Email Notifications',
    'author': 'Kotura Derrick Amu',
    'depends': ['base', 'mail', 'website', 'sms'],
    'data': [
        'security/ir.model.access.csv',
        'views/national_id_views.xml',
        'views/menu.xml',
        'wizards/national_id_reject_wizard_view.xml',
        'templates/application_form.xml',
    ],
    'installable': True,
    'application': True,
}

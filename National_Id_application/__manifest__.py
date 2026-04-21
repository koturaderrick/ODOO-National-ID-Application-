{
    'name': 'National ID Registration Module',
    'version': '1.0',
    'category': 'Registration',
    'summary': 'Online National ID Application with Workflow and Notifications',
    'author': 'Kotura Derrick Amu',
    'depends': ['base', 'website', ],
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

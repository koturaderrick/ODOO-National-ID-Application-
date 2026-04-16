{
    'name': 'National ID Registration Module',
    'version': '1.0',
    'category': 'Registration',
    'summary': 'Online National ID Application Processing',
    'description': """
        National ID Registration System based on NIRA Form 3
    """,
    'author': 'Kotura Derrick Amu',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/national_id_views.xml',
        'views/menu.xml',
        'wizards/national_id_reject_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

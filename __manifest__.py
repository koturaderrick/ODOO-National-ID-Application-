{
    'name': 'National Identity Card Registration',
    'version': '1.0',
    'summary': 'National Identity Card Registration',
    'category': 'Registration',
    'author': 'Kola Tech Kotura Derrick Amu',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/national_id_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}

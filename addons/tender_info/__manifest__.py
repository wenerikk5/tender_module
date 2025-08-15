# -*- coding: utf-8 -*-
{
    'name': "Тендеры",
    'summary': "Информация о тендерах портала ЕТП ГПБ",

    'description': """
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Services',
    'version': '0.1',

    'installable': True,
    'application': True,

    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/procedure_views.xml',
        'views/lot_views.xml',
        'views/participant_views.xml',
        'wizards/import_wizard_views.xml',
        'views/menu.xml',
    ],
}


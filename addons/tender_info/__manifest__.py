# -*- coding: utf-8 -*-
{
    'name': "Тендеры",

    'summary': "Информация о тендерах портала ЕТП ГПБ",

    'description': """
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
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

    # 'demo': [
    #     'demo/demo.xml',
    # ],
}


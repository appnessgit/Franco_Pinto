# -*- coding: utf-8 -*-
{
    'name': "sale purchase backdated",

    'summary': """This Module managed sale and purchase transaction backdated """,

    'description': """This Module managed sale and purchase transaction backdated""",

    'author': "Appness Tech.",
    'website': "http://www.appness.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','sale_stock','contacts'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/views.xml',
        'views/sale_approve_all.xml',
        'views/res.partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

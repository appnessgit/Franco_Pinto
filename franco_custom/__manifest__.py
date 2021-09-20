# -*- coding: utf-8 -*-
{
    'name': "franco_custom",

    'summary': """
        invoice customization""",

    'description': """
        -Fields from datetime to date
        -Selecting vendor Just in vendors list
        -Selecting customer Just in Customers list-
    """,

    'author': "Appness",
    'website': "http://www.appness.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','stock','account'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/sales.xml',
        'reports/dpi_header_layout.xml',
        'reports/purchase_report.xml',
        'reports/purchase_report_template.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}

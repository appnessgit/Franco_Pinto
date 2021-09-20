# -*- coding: utf-8 -*-
{
    'name': "Stock Move Back Date",
    'summary': """change validation date with scheduled date for stock transfers / picking / receipt / delivery order.""",
    'description': """
        The problem
        ===========
        In Odoo, when you validate a stock transfer, Odoo applies the current time for the transfer date automatically 
        which is sometimes not what you want. For example, you input data for the past.
        
        The solution
        ============
        This module change validation date with scheduled date for stock transfers.
        
        The scheduled date you input here will also be used for accounting entry's date if the product is configured with automated stock valuation.
        
    """,

    'author': 'Appness Technology',
    'website': 'https://appness.net',
    'category': 'Warehouse',
    'version': '14.0.1',
    'depends': ['stock_account','purchase_stock'],
    'data': [
        # 'views/stock_picking_view.xml'
    ],
    'application': False,
    'installable': True,
    'images': [],
    'license': 'OPL-1',
}

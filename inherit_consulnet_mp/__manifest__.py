# -*- coding: utf-8 -*-
{
    'name': "Consulnet HERENCIA",
    'summary': """
        Herencia para Consulnet
	""",
    'description': """
        Herencias Modulos Base Consulnet
    """,
    'author': "Cesar Chirinos",
    'website': "http://www.consulnet.cl",
    'category': 'Geenral o Base',
    'version': '0.1',
    'depends': ['base', 'sale'],
    'data': [
        # 'security/ir.model.access.csv',
        #'views/res_company_views.xml',
        'views/res_partner_view.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}

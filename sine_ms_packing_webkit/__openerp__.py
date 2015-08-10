# -*- coding: utf-8 -*-


{
    'name': 'Picking reports for Motoscoot using Webkit Library',
    'version': '1.0.1',
    'category': 'Reports/Webkit',
    'description': """
Replaces the legacy rml picking Order report by brand new webkit reports.
    """,
    'author': "David Hernandez. Sinergiainformatica.net)",
    'website': 'http://sinergiainforatica.net',
    'depends': ['base',
                'report_webkit',
                'base_headers_webkit',
                'stock',
                'delivery'],
    'data': ['report.xml'],
    'installable': True,
    'auto_install': False,
}
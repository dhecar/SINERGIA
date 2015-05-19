# -*- coding: utf-8 -*-
{
    "name" : "Estension de modulo productos para incorporar modelos de Scooter",
    "version" : "7.0",
    "author" : "David Hernández",
    "category" : "Generic Modules/Others",
    "website" : "http://sinergiainformatica.net",
    "description": "Extensión módulo productos para relacionarlos con modelos de Scooter",
    "depends" : ["product"],
    "update_xml" : ["product_motoscoot_view.xml", "partner_motoscoot_view.xml", "scooter_models_view.xml", "marcas_scooter_view.xml", "asociaciones_view.xml"],

    "data": ['security/security.xml', 'security/ir.model.access.csv'],
    "active": True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

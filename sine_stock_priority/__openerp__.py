# -*- coding: utf-8 -*-
{
    "name": "Stock warehouse priority",
    "version": "7.0",
    "author": "David Hernández",
    "category": "Generic Modules/Others",
    "website": "http://sinergiainformatica.net",
    "description": "Extension que añade una validación en los envios internos si el stock de origen "
                   "se queda por debajo de 1 en el momento de validar el envio, dando prioridad de stock"
                   "al almacén local",
    "depends": ["product", "stock_location", "stock"],
    "update_xml": [],
    "data": ['stock_priority_wfl.xml', 'security/security.xml', 'security/ir.model.access.csv'],
    "active": True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

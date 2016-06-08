# -*- coding: utf-8 -*-
{
    "name": "Módulo para incorporar modelos de Scooter",
    "version": "7.0",
    "author": "David Hernández",
    "category": "Generic Modules/Others",
    "website": "http://sinergiainformatica.net",
    "description": """
                   * Relaciona los productos con los modelos de moto compatibles

                   * Añade campo de relación con los modelos en la ficha de producto

                   * Añade campo de relación en la ficha de cliente

                   * Discrimina las lineas de la orden en función de si el producto es o no compatible con el modelo de del cliente en la orden

                    * Añade campos de búsqueda por tipo/marca/modelo en los productos""",
    "depends": ["product", "sale"],
    "data": ['security/security.xml', 'security/ir.model.access.csv'],
    "update_xml": ["views/marcas_scooter_view.xml",
                   "views/product_motoscoot_view.xml",
                   "views/partner_motoscoot_view.xml",
                   "views/scooter_models_view.xml",
                   "views/asociaciones_view.xml",
                   "views/sale_view.xml"],

    "active": True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

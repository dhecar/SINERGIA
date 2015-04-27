# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.magentoerpconnect.product import ProductImportMapper
from .backend import magento_myversion

@magento_myversion
class MyProductImportMapper(ProductImportMapper):
    _inherit = 'product.product'
    direct = ProductImportMapper.direct + [('msrp', 'pvp')]
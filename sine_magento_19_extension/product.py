# -*- coding: utf-8 -*-

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,)
from openerp.addons.magentoerpconnect.product import ProductImportMapper
from openerp.addons.connector.exception import MappingError
from .backend import magento_myversion


@magento_myversion
class MyProductImportMapper(ProductImportMapper):
    _inherit = 'product.product'

    direct = ProductImportMapper.direct + [
        ('msrp', 'pvp_fabricante'),
        ('status', 'internet')]






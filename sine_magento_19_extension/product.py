# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp.addons.connector.unit.mapper import (mapping, only_create)
from openerp.addons.magentoerpconnect.product import ProductImportMapper
from openerp.addons.connector.exception import MappingError
from .backend import magento_myversion

@magento_myversion
class MyProductImportMapper(ProductImportMapper):
    _inherit = 'product.product'

    direct = ProductImportMapper.direct + [('msrp', 'pvp_fabricante')]

    @only_create
    @mapping
    def prod_brand_id(self, record):
        binder = self.get_binder_for_model('magento.product.product')
        brand_id = binder.to_openerp(record['manufacturer'], unwrap=False)

        """ product.product_brand_id  m2o to product_brand """
        return {'product_brand_id': brand_id}



    #direct = ProductImportMapper.direct + [('manufacturer', 'product_brand_id')]

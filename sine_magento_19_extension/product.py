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

    direct = ProductImportMapper.direct + [('msrp', 'pvp_fabricante')]

    @mapping
    def prod_brand_id(self, record):
        prod_brand = record['manufacturer']
        binder = self.get_binder_for_model('magento.product.manufacturer')
        brand_id = binder.to_openerp(record['manufacturer'], unwrap=True)

        prod_brand_ids = []
        main_brand_id = None

        if prod_brand is None:
                raise MappingError("The product brand with "
                                   "magento id %s is not imported." %
                                   prod_brand)

        if prod_brand:

            prod_brand_ids.append(brand_id)

            if prod_brand_ids:
                main_brand_id = prod_brand_ids.pop(0)

            result = main_brand_id
            print result
            return result




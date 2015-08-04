# -*- coding: utf-8 -*-

from openerp.addons.connector.unit.mapper import (mapping, only_create)
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

        prod_brand_ids = []
        main_brand_id = None

        if prod_brand:
            brand_id = binder.to_openerp(record['manufacturer'], unwrap=True)
            if prod_brand is None:
                raise MappingError("The product brand with "
                                   "magento id %s is not imported." %
                                   prod_brand)

            prod_brand_ids.append(brand_id)

        if prod_brand_ids:
            main_brand_id = prod_brand_ids.pop(0)

       # if main_brand_id is None:
       #     default_categ = self.backend_record.default_category_id
       #    if default_categ:
       #         main_categ_id = default_categ.id

        result = main_brand_id

        #if prod_brand_id:  # OpenERP assign 'All Products' if not specified
        #    result['product_brand_id'] = main_brand_id

        return result


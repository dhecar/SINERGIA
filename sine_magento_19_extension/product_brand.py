# -*- coding: utf-8 -*-
##############################################################################
# Author: David Hernández
# Sinergiainformatica.net. 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import xmlrpclib
from openerp.osv import orm, fields

from openerp.addons.magentoerpconnect.unit.backend_adapter import (GenericAdapter,
                                                           MAGENTO_DATETIME_FORMAT,)

from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper, )
from .backend import magento_myversion

_logger = logging.getLogger(__name__)


class magento_product_manufacturer(orm.Model):
    _name = 'magento.product.manufacturer'
    _inherit = 'magento.binding'
    _inherits = {'product.brand': 'openerp_id'}
    _description = 'Magento Product Manufacturer'

    _columns = {
        'openerp_id': fields.many2one('product.brand',
                                      string='Product Brand',
                                      required=True,
                                      ondelete='cascade'),
        'description': fields.text('Description', translate=True),
        'magento_brand_id': fields.many2one(
            'magento.product.manufacturer',
            string='Magento Manufacturer',
            ondelete='cascade'),
    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A Product Brand with the same ID on Magento already exists.'),
    ]


class product_brand(orm.Model):
    _inherit = 'product.brand'

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.product.manufacturer', 'openerp_id',
            string="Magento Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['magento_bind_ids'] = False
        return super(product_brand, self).copy_data(cr, uid, id,
                                                    default=default,
                                                    context=context)


@magento_myversion
class ProductProductAdapter(GenericAdapter):
    _model_name = 'magento.product.product'
    _magento_model = 'catalog_product'
    _admin_path = '/{model}/edit/id/{id}'

    def _call(self, method, arguments):
        try:
            return super(ProductProductAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Magento API
            # when the product does not exist
            if err.faultCode == 101:
                raise IDMissingInBackend
            else:
                raise

    def search(self, filters=None, from_date=None, to_date=None):
        """ Search records according to some criteria
        and returns a list of ids

        :rtype: list
        """
        if filters is None:
            filters = {}
        dt_fmt = MAGENTO_DATETIME_FORMAT
        if from_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date.strftime(dt_fmt)
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date.strftime(dt_fmt)
        # TODO add a search entry point on the Magento API
        return [int(row['product_id']) for row
                in self._call('%s.list' % self._magento_model,
                              [filters] if filters else [{}])]

    def read(self, id, storeview_id=None, attributes=None):
        """ Returns the information of a record

        :rtype: dict
        """
        return self._call('ol_catalog_product.info',
                          [int(id), storeview_id, attributes, 'id'])

    def write(self, id, data, storeview_id=None):
        """ Update records on the external system """
        # XXX actually only ol_catalog_product.update works
        # the PHP connector maybe breaks the catalog_product.update
        return self._call('ol_catalog_product.update',
                          [int(id), data, storeview_id, 'id'])

    def get_images(self, id, storeview_id=None):
        return self._call('product_media.list', [int(id), storeview_id, 'id'])

    def read_image(self, id, image_name, storeview_id=None):
        return self._call('product_media.info',
                          [int(id), image_name, storeview_id, 'id'])

    def update_inventory(self, id, data):
        # product_stock.update is too slow
        return self._call('oerp_cataloginventory_stock_item.update',
                          [int(id), data])

    def get_manufacturer(self, id, manufacturer, storeview_id=None):
        return self._call('ol_catalog_product.info',
                          [int(id), manufacturer, storeview_id, 'id'])



@magento_myversion
class ManufacturerProductImportMapper(ImportMapper):
    _model_name = 'magento.product.manufacturer'

    @mapping
    def manufacturer(self, record):

        return {'name': record.get('manufacturer')}




@magento_myversion
class ProductImportMapper(ImportMapper):
    _model_name = 'magento.product.product'

    @mapping
    def prod_manufacturer(self, record):
        """Manufacturer linked to the product"""
        mapper = self.get_connector_unit_for_model(ManufacturerProductImportMapper)
        return mapper.map_record(record).values()


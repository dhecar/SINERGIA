# -*- coding: utf-8 -*-
##############################################################################
# Author : David Hernandez. 2015. http://sinergiainformatica.net
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm
import xmlrpclib
import time
from openerp import netsvc
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class WyomindConfig(osv.osv):
    _name = 'wyomind.config'
    _description = 'Configuration for Wyomind API stock update'
    _table = 'wyomind_config'
    _columns = {
        'url': fields.char('Api Url', help="Example --> http://WEBSITE/index.php/api/xmlrpc/", size=60),
        'apiuser': fields.char('Api User', size=15),
        'apipass': fields.char('Api Password', size=15)
    }


WyomindConfig()


class stock_change_product_qty(osv.osv_memory):
    _inherit = "stock.change.product.qty"

    def change_product_qty(self, cr, uid, ids, context=None):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context')

        inventry_obj = self.pool.get('stock.inventory')
        inventry_line_obj = self.pool.get('stock.inventory.line')
        prod_obj_pool = self.pool.get('product.product')

        res_original = prod_obj_pool.browse(cr, uid, rec_id, context=context)
        for data in self.browse(cr, uid, ids, context=context):
            if data.new_quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Quantity cannot be negative.'))
            inventory_id = inventry_obj.create(cr, uid, {'name': _('INV: %s') % tools.ustr(res_original.name)},
                                               context=context)
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': data.new_quantity,
                'location_id': data.location_id.id,
                'product_id': rec_id,
                'product_uom': res_original.uom_id.id,
                'prod_lot_id': data.prodlot_id.id
            }

            inventry_line_obj.create(cr, uid, line_data, context=context)

            inventry_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventry_obj.action_done(cr, uid, [inventory_id], context=context)

            # Update Stock in Magento
            conf_obj = self.pool.get('wyomind.config')
            conf_ids = conf_obj.search(cr, uid, [('id', '=', 1)])
            for i in conf_obj.browse(cr, uid, conf_ids):
                url = i.url
                user = i.apiuser
                passw = i.apipass

            # Connection
            proxy = xmlrpclib.ServerProxy(url, allow_none=True)
            session = proxy.login(user, passw)

            def get_mag_prod_id(self, cr, uid, ids, context=None):
                mag_prod_obj = self.pool.get('magento.product.product')
                result = {}
                mag_prod_ids = mag_prod_obj.search(cr, uid, [('openerp_id', '=', rec_id)],
                                                   context=context)

                if mag_prod_ids:
                    for prod in mag_prod_obj.browse(cr, uid, mag_prod_ids, context=context):
                        result = prod.magento_id

                    return result

            # we hardcoded the mapping local-remote warehouse

            location = 0
            if data.location_id.id == 12:
                location = 2
            if data.location_id.id == 15:
                location = 4
            if data.location_id.id == 19:
                location = 3

            data_basic = {'quantity_in_stock': data.new_quantity,
                          'manage_stock': 1,
                          'backorder_allowed': 0,
                          'use_config_setting_for_backorders': 0,

                          }

            proxy.call(session, 'advancedinventory.setMultistock',
                       (get_mag_prod_id(self, cr, uid, ids, context=context), True))
            proxy.call(session, 'advancedinventory.setData', (get_mag_prod_id(self, cr, uid, ids, context=context),
                                                              location, data_basic)),

        return {}


stock_change_product_qty()


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def do_partial(self, cr, uid, ids, context=None):
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)
        partial = self.browse(cr, uid, ids[0], context=context)
        # Wyomind Config
        conf_obj = self.pool.get('wyomind.config')
        conf_ids = conf_obj.search(cr, uid, [('id', '=', 1)])
        for x in conf_obj.browse(cr, uid, conf_ids):
            url = x.url
            user = x.apiuser
            passw = x.apipass

            # Connection
            proxy = xmlrpclib.ServerProxy(url, allow_none=True)
            session = proxy.login(user, passw)
            multicall = xmlrpclib.MultiCall(proxy)
        # Wyomind stock update

        for wizard_line in partial.move_ids:

            """Locations hardcoded"""
            # TODO put locations in config file

            location = 0
            if wizard_line.location_id.id == 12:
                location = 2
            if wizard_line.location_id.id == 15:
                location = 4
            if wizard_line.location_id.id == 19:
                location = 3

            location2 = 0
            if wizard_line.location_dest_id.id == 12:
                location2 = 2
            if wizard_line.location_dest_id.id == 15:
                location2 = 4
            if wizard_line.location_dest_id.id == 19:
                location2 = 3

            """ Update origin stock and dest stock locations"""
            if partial.picking_id.type == 'internal':
                # product stock origin
                cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                       location_id =%s AND product_id = %s""" %
                           (wizard_line.location_id.id, wizard_line.product_id.id))
                q_orig = cr.fetchone()[0]

                # product stock dest
                cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                           location_id =%s AND product_id = %s""" %
                           (wizard_line.location_dest_id.id, wizard_line.product_id.id))
                q_dest = cr.fetchone()[0]

                # magento id
                cr.execute('SELECT magento_id'
                           ' FROM magento_product_product'
                           ' WHERE openerp_id =%s' % wizard_line.product_id.id)
                mag_id = cr.fetchone()[0]

                # Only internal movements are computed
                data_basic = {'quantity_in_stock': q_orig,
                              'manage_stock': 1,
                              'backorder_allowed': 0,
                              'use_config_setting_for_backorders': 0
                              }

                proxy.call(session, 'advancedinventory.setData',
                           (mag_id, location, data_basic))

                data_basic2 = {'quantity_in_stock': q_dest,
                               'manage_stock': 1,
                               'backorder_allowed': 0,
                               'use_config_setting_for_backorders': 0
                               }

                proxy.call(session, 'advancedinventory.setMultistock', (mag_id, True))
                proxy.call(session, 'advancedinventory.setData',
                           (mag_id, location2, data_basic2))

            """ Update dest stock location"""
            if partial.picking_id.type == 'in':
                # If product is linked to magento
                if wizard_line.product_id.magento_bind_ids:
                    # product stock
                    cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                       location_id =%s AND product_id = %s""" %
                               (wizard_line.location_dest_id.id, wizard_line.product_id.id))
                    q = cr.fetchone()[0]

                    # magento id
                    cr.execute('SELECT magento_id'
                               ' FROM magento_product_product'
                               ' WHERE openerp_id =%s' % wizard_line.product_id.id)
                    mag_id = cr.fetchone()[0]

                    data_basic = {'quantity_in_stock': q,
                                  'manage_stock': 1,
                                  'backorder_allowed': 0,
                                  'use_config_setting_for_backorders': 0
                                  }

                    proxy.call(session, 'advancedinventory.setMultistock', (mag_id, True))
                    proxy.call(session, 'advancedinventory.setData',
                               (mag_id, location2, data_basic))

            """ Update origin stock location"""
            if partial.picking_id.type == 'out':
                # If product is linked to magento
                if wizard_line.product_id.magento_bind_ids:
                    cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                               location_id =%s AND product_id = %s""" %
                               (wizard_line.location_id.id, wizard_line.product_id.id))
                    q = cr.fetchone()[0]

                    # magento id

                    cr.execute('SELECT magento_id'
                               ' FROM magento_product_product'
                               ' WHERE openerp_id =%s' % wizard_line.product_id.id)
                    mag_id = cr.fetchone()[0]

                    # Out movements are computed.
                    data_basic = {'quantity_in_stock': q,
                                  'manage_tock': 1,
                                  'backorder_allowed': 0,
                                  'use_config_setting_for_backorders': 0}

                    proxy.call(session, 'advancedinventory.setMultistock', (mag_id, True))
                    proxy.call(session, 'advancedinventory.setData',
                               (mag_id, location, data_basic))

        return res


stock_partial_picking()

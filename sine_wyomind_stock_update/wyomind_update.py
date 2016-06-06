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
from openerp import SUPERUSER_ID
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


class WyomindStockSync(osv.TransientModel):
    _name = 'wyomind.sync'
    _description = 'Syncronize Stock'

    def wyomind_sync(self, cr, ids, uid, context=None):
        # Wyomind Config

        db_obj = self.pool['base.external.dbsource']

        cr.execute(""" SELECT qty , product_id , location_id FROM stock_report_prodlots
                        WHERE (location_id ='12' OR location_id ='19' OR location_id='15')
                         ORDER BY location_id""")
        res = cr.dictfetchall()
        result = {}
        conf_obj = self.pool.get('wyomind.config')
        conf_ids = conf_obj.search(cr, uid, [('id', '=', 1)])
        for x in conf_obj.browse(cr, uid, conf_ids):
            url = x.url
            user = x.apiuser
            passw = x.apipass

            # Connection
        proxy = xmlrpclib.ServerProxy(url, allow_none=True)
        session = proxy.login(user, passw)

        for r in res:
            """ ONly Sync linked products """
            cr.execute('SELECT magento_id'
                       ' FROM magento_product_product'
                       ' WHERE openerp_id =%s' % r['product_id'])
            mag_id = cr.fetchone()
            # If product is linked to magento
            if mag_id is not None:

                if r['location_id'] == 12:
                    ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, r['product_id'], r['location_id'],
                                           context=context)

                    q = r['qty'] - ads

                else:
                    q = r['qty']

                data_basic = {'quantity_in_stock': q,
                              'manage_stock': 1,
                              'backorder_allowed': 0,
                              'use_config_setting_for_backorders': 0
                              }

                location = 0
                if r['location_id'] == 12:
                    location = 2
                if r['location_id'] == 15:
                    location = 4
                if r['location_id'] == 19:
                    location = 3

                proxy.call(session, 'advancedinventory.setData',
                           (mag_id[0], location, data_basic))

        return result


WyomindStockSync()


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def action_done(self, cr, uid, ids, context=None):
        tiempo_inicial = time.time()
        res = super(stock_move, self).action_done(cr, uid, ids, context=context)
        # REMOTE
        db_obj = self.pool['base.external.dbsource']

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

        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state == "draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'done':
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)

                # Wyomind stock update
        for move in self.browse(cr, uid, ids, context=context):

            """Locations hardcoded"""
            # TODO put locations in config file

            location = 0
            if move.location_id.id == 12:
                location = 2
            if move.location_id.id == 15:
                location = 4
            if move.location_id.id == 19:
                location = 3

            location2 = 0
            if move.location_dest_id.id == 12:
                location2 = 2
            if move.location_dest_id.id == 15:
                location2 = 4
            if move.location_dest_id.id == 19:
                location2 = 3

            """ Update dest stock location for partial in movements"""
            # If product is linked to magento
            if move.product_id.magento_bind_ids and location2 != 0:
                # product stock
                cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                                    location_id =%s AND product_id = %s""" %
                           (move.location_dest_id.id, move.product_id.id))
                qty = cr.fetchone()[0]

                # CASE GRN
                if move.location_dest_id.id == 12:
                    ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, move.product_id.id,
                                           move.location_dest_id.id, context=context)
                    q = qty - ads
                else:
                    q = qty

                # magento id
                cr.execute('SELECT magento_id'
                           ' FROM magento_product_product'
                           ' WHERE openerp_id =%s' % move.product_id.id)
                mag_id = cr.fetchone()[0]

                data_basic = {'quantity_in_stock': q,
                              'manage_stock': 1,
                              'backorder_allowed': 0,
                              'use_config_setting_for_backorders': 0
                              }

                proxy.call(session, 'advancedinventory.setData',
                           (mag_id, location2, data_basic))

            """ Update origin stock location for partial out movements"""
            # If product is linked to magento
            if move.product_id.magento_bind_ids and location != 0:
                # product stock
                cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                                location_id =%s AND product_id = %s""" %
                           (move.location_id.id, move.product_id.id))
                qty = cr.fetchone()[0]

                # CASE GRN
                if move.location_id.id == 12:
                    ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, move.product_id.id,
                                           move.location_id.id, context=context)
                    q = qty - ads
                else:
                    q = qty

                # magento id
                cr.execute('SELECT magento_id'
                           ' FROM magento_product_product'
                           ' WHERE openerp_id =%s' % move.product_id.id)
                mag_id = cr.fetchone()[0]

                data_basic = {'quantity_in_stock': q,
                              'manage_stock': 1,
                              'backorder_allowed': 0,
                              'use_config_setting_for_backorders': 0
                              }

                proxy.call(session, 'advancedinventory.setData',
                           (mag_id, location, data_basic))

            tiempo_final = time.time()
            tiempo_ejecucion = tiempo_final - tiempo_inicial
            print ' stock_move', tiempo_ejecucion

        return res


class InvoiceSaleOrder(osv.TransientModel):
    _inherit = 'sale.order.invoiced'

    def do_invoice(self, cr, uid, ids, context=None):
        res = super(InvoiceSaleOrder, self).do_invoice(cr, uid, ids, context=context)
        sale_obj = self.pool['sale.order']
        sale_id = context.get('active_id', [])
        db_obj = self.pool['base.external.dbsource']
        db_id = db_obj.search(cr, uid, [
            ('name', '=', 'Sale_To_Invoice')
        ], context=context)

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

        location = 12
        if db_id:
            if sale_id:
                for sale in sale_obj.browse(cr, uid, [sale_id],
                                            context=context):
                    for line in sale.order_line:
                        if line.product_id.magento_bind_ids:
                            cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                                   location_id =%s AND product_id = %s""" %
                                       (location, line.product_id.id))

                            qty = cr.fetchone()[0]
                            # CASE GRN
                            ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, line.product_id.id,
                                                   location, context=context)

                            q = qty - ads
                            cr.execute('SELECT magento_id'
                                       ' FROM magento_product_product'
                                       ' WHERE openerp_id =%s' % line.product_id.id)
                            mag_id = cr.fetchone()[0]

                            # Out movements are computed.
                            data_basic = {'quantity_in_stock': q,
                                          'manage_stock': 1,
                                          'backorder_allowed': 0,
                                          'use_config_setting_for_backorders': 0}

                            proxy.call(session, 'advancedinventory.setData',
                                       (mag_id, 2, data_basic))
        return res


InvoiceSaleOrder()

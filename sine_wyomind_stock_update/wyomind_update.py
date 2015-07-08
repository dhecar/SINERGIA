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

_logger = logging.getLogger(__name__)


class WyomindConfig(osv.osv):
    _name = 'wyomind.config'
    _description = 'Configuration for Wyomind API stock update'
    # _table = 'wyomind_config'
    _columns = {
        'url': fields.char('Api Url', help="Example --> http://WEBSITE/index.php/api/xmlrpc/", size=60),
        'apiuser': fields.char('Api User', size=15),
        'apipass': fields.char('Api Password', size=15)
    }


WyomindConfig()


class stock_move(osv.osv):
    _inherit = 'stock.move'
    _description = 'Update the stock from Openerp to Magento (Advanced Inventory) when the move' \
                   ' go to done state'

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
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
            if move.state in ['done', 'cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                # Downstream move should only be triggered if this move is the last pending upstream move
                other_upstream_move_ids = self.search(cr, uid, [('id', 'not in', move_ids),
                                                                ('state', 'not in', ['done', 'cancel']),
                                                                ('move_dest_id', '=', move.move_dest_id.id)],
                                                      context=context)
                if not other_upstream_move_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            self._update_average_price(cr, uid, move, context=context)
            self._create_product_valuation_moves(cr, uid, move, context=context)
            if move.state not in ('confirmed', 'done', 'assigned'):
                self.action_confirm(cr, uid, [move.id], context=context)

            self.write(cr, uid, [move.id],
                       {'state': 'done',
                        'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)},
                       context=context)

            # Update xmlrpc. Wyomind Advanced Inventory
            # Get configuration from wyomind_config

            conf = self.pool.get('wyomind.config').browse(cr, uid, uid)
            url = conf.url
            user = conf.apiuser
            passw = conf.apipass

            # Connection
            proxy = xmlrpclib.ServerProxy(url, allow_none=True)
            session = proxy.login(user, passw)

            # We get the product qty from stock_report_prodlots .
            def get_stock(self, cr, uid, ids, context=None):
                stock_prod_obj = self.pool.get('stock.report.prodlots')
                # TODO search only movements in internal stock locations
                for prod_id in move_ids:
                    result = {}
                    stock_prod_ids = stock_prod_obj.search(cr, uid, [('product_id', '=', move.product_id.id),
                                                                 ('location_id', '=', move.location_dest_id.id)],
                                                       context=context)

                    if stock_prod_ids:
                        for i in stock_prod_obj.browse(cr, uid, stock_prod_ids, context=context):
                            result = i.qty

                return result

            # We get magento product_id

            def get_mag_prod_id(self, cr, uid, ids, context=None):
                mag_prod_obj = self.pool.get('magento.product.product')
                for magento_prod_id in move_ids:
                    result = {}
                    mag_prod_ids = mag_prod_obj.search(cr, uid, [('openerp_id', '=', move.product_id.id)],
                                                   context=context)

                    if mag_prod_ids:
                        for prod in mag_prod_obj.browse(cr, uid, mag_prod_ids, context=context):
                            result = prod.magento_id
                            print result

                return result

            # we hardcode the mapping local-remote warehouse

            location = 2
            if move.location_id == 12:
                location = 2
            if move.location_id == 15:
                location = 3
            if move.location_id == 19:
                location = 4

            data_basic = {'quantity_in_stock': get_stock(self, cr, uid, ids, context=context),
                          'manage_stock': 1,
                          'backorder_allowed': 0,
                          'use_config_setting_for_backorders': 1}

            proxy.call(session, 'advancedinventory.setData', (get_mag_prod_id(self, cr, uid, ids, context=context),
                                                              location, data_basic))

            print data_basic

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True


stock_move()
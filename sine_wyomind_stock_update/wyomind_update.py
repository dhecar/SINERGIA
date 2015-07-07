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


class WyomindConfig(osv.osv):
    _name = 'wyomind.config'
    _description = 'Configuration for Wyomind API stock update'
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

    def do_partial(self, cr, uid, ids, partial_datas, context=None):

        res = super(stock_move, self).do_partial(cr, uid, ids, partial_datas, context=context)
        conf = self.pool.get('wyomind.config')
        url = conf.url
        user = conf.apiuser
        passw = conf.apipass

        # Connection
        proxy = xmlrpclib.ServerProxy(url, allow_none=True)
        session = proxy.login(user, passw)

        for move in self.browse(cr, uid, ids, context=context):

            if move.state == 'done':
                # We get the product qty, location_dest_id , mag_prod_id .
                qty = move.product_qty
                mag_prod_id = move.product_id.magento_bind_ids.magento_id
                location = move.location_dest_id.id

                data = {'quantity_in_stock': qty,
                        'manage_stock': 1,
                        'backorder_allowed': 0,
                        'use_config_setting_for_backorders': 1}

                proxy.call(session, 'advancedinventory.setData', (mag_prod_id, location, data))

        return res


stock_move()
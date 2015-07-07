# -*- coding: utf-8 -*-
##############################################################################
#
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
from osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


class StockPicking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Transfer'),
            ('done', 'Transferred'),
            ('to_be_validate', 'Waiting Validation'),
        ], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: not confirmed yet and will not be scheduled until confirmed\n
            * Esperando Validacion: One stock manager have to validate this movement\n
            * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
            * Waiting Availability: still waiting for the availability of products\n
            * Ready to Transfer: products reserved, simply waiting for confirmation.\n
            * Transferred: has been processed, can't be modified or cancelled anymore\n
            * Cancelled: has been cancelled, can't be confirmed anymore"""
        ),

    }

    def action_assign_wkf(self, cr, uid, ids, context=None):
        to_update = []
        for picking in self.browse(cr, uid, ids):
            if picking.type == 'internal':
                for move in picking.move_lines:
                    stock_prod_obj = self.pool.get('stock.report.prodlots')
                    stock_prod_ids = stock_prod_obj.search(cr, uid,
                                                           [('product_id', '=', move.product_id.id),
                                                            ('location_id', '=', move.location_id.id)])
                    if stock_prod_ids:
                        for i in stock_prod_obj.browse(cr, uid, stock_prod_ids, context=context):
                            if i.qty < 0:
                                raise osv.except_osv('No hay stock de este producto!',
                                                     'El producto  %s tiene un stock de %d! y estas intentando '
                                                     'enviar %d !!, contacta con el administrador '
                                                     % (move.product_id.name, i.qty, move.product_qty))

                            elif i.qty - move.product_qty < 1:
                                if picking.state != 'assigned':
                                    to_update.append(picking.id)
                                if to_update:
                                    self.write(cr, uid, to_update, {'state': 'to_be_validate'})

                            else:
                                if picking.state != 'assigned':
                                    to_update.append(picking.id)
                                if to_update:
                                    self.write(cr, uid, to_update, {'state': 'assigned'})

                        return True

    def button_validate(self, cr, uid, ids, context=None):
        """ Changes picking state to assigned.
        @return: True
        """
        to_update = []
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state != 'assigned':
                to_update.append(pick.id)
        if to_update:
            self.write(cr, uid, to_update, {'state': 'assigned'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Changes picking state to cancel.
        @return: True
        """
        for pick in self.browse(cr, uid, ids, context=context):
            ids2 = [move.id for move in pick.move_lines]
            self.pool.get('stock.move').action_cancel(cr, uid, ids2, context)
        self.write(cr, uid, ids, {'state': 'cancel', 'invoice_state': 'none'})
        return True


StockPicking()

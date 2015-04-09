# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
                                diferencia = i.qty - move.product_qty

                                raise osv.except_osv('El envio dejara sin existencias el almacen !',
                                                     'El producto  %s tiene un stock de %d! y estas intentando '
                                                     'enviar %d. El stock bajara a %d !!,contacta con el administrador'
                                                     'para que valide el envio'
                                                     % (move.product_id.name, i.qty, move.product_qty, diferencia))
                            else:
                                if picking.state != 'assigned':
                                    to_update.append(picking.id)
                                if to_update:
                                    self.write(cr, uid, to_update, {'state': 'assigned'})

                        return True


StockPicking()

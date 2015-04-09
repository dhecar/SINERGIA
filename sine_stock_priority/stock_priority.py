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

        for picking in self.browse(cr, uid, ids):
            if picking.type == 'internal':
                for move in picking.move_lines:

                    stock_prod_obj = self.pool.get('stock.report.prodlots')
                    stock_prod_ids = stock_prod_obj.search(cr, uid,
                                                           [('product_id', '=', move.product_id.id)])
                    if stock_prod_ids:
                        for i in stock_prod_obj.browse(cr, uid, stock_prod_ids, context=context):
                            if i.qty == 1:
                                raise osv.except_osv('Ultimo producto en almacen !',
                                                     'El producto  %s tiene un stock de %d! y no puede enviarse,'
                                                     'contacta con el administrador ' % (move.product_id.name, i.qty))

        return True


StockPicking()

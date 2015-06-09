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
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


class product_product(osv.osv):
    def copy_fitments(self, cr, uid, ids, context=None):
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.select_origin:
                other_ids = [scooters_ids.id for scooters_ids in prod.select_origin.scooters_ids]
                vals = {'scooters_ids': [(6, 0, other_ids)]}
                prod.write(vals)

    def _find_products_by_scooter(self, cr, uid, obj, name, args, context):
        new_args = []
        for (field, operator, value) in args:
            if field == 'scooter_type':
                new_args.append(('type', operator, value))
            elif field == 'scooter_brand_id':
                new_args.append(('brand_id', operator, value))
            elif field == 'scooter_model_id':
                new_args.append(('model_id', operator, value))

        asociaciones_ids = self.pool['scooter.asociaciones'].search(cr, uid, new_args)
        product_ids = self.pool['product.product'].search(cr, uid, [('scooters_ids', 'in', asociaciones_ids)])
        return [('id', 'in', product_ids)]


    def _null(self, ):

        val = {id: '' for id in ids}
        return val


    _name = 'product.product'
    _inherit = 'product.product'

    _columns = {
        'scooters_ids': fields.many2many('scooter.asociaciones', 'scooter_compat_with_product_rel', 'product_id',
                                         'scooter_id', 'scooter models'),
        'select_origin': fields.many2one('product.product', 'Origin Product Fitments', domain=[('sale_ok', '=', True)],
                                         change_default=True),

        'scooter_type': fields.function(_null, fnct_search=_find_products_by_scooter, type='char',
                                        string='Scooter Type', store=True),
        'scooter_brand_id': fields.function(_null, fnct_search=_find_products_by_scooter, type='char',
                                            string='Scooter Brand', store=True),
        'scooter_model_id': fields.function(_null, fnct_search=_find_products_by_scooter, type='char',
                                            string='Scooter Model', store=True)
    }


product_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
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

from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


class product_product(osv.osv):

    def copy_fitments(self, cr, uid, ids,  context=None):
        for prod in self.browse(cr, uid, ids, context=context):
            if prod.select_origin:
                other_prod = self.browse(cr, uid, prod.select_origin.id, context=context)
                other_ids = [scooters_ids.id for scooters_ids in other_prod.scooters_ids]
                vals = {'scooters_ids': [(6, 0, other_ids)]}
                prod.write(vals)

    _name = 'product.product'
    _inherit = 'product.product'

    _columns = {
        'scooters_ids': fields.many2many('scooter.asociaciones', 'scooter_compat_with_product_rel', 'product_id',
                                         'scooter_id', 'scooter models'),
        'select_origin': fields.many2one('product.product', 'Origin Product Fitments', domain=[('sale_ok', '=', True)],
                                         change_default=True),

    }

product_product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

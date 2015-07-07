# -*- coding: utf-8 -*-
##############################################################################
# Sinergiainformatica.net
# David Hernández. 2015
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
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


class sale_order_line(osv.osv):

    """ Search in the customer form for the scooter model and put the sale order line in green if the
    product is compatible and in red if not is compatible with their scooter"""

    def _get_customer_model(self, cr, uid, ids, fields, arg, context):

        def comp(list1, list2):
            for val in list1:
                if val in list2:
                    return True
            return False

        res = {}

        for i in ids:

            prod_models_ids = self.browse(cr, uid, i,  context).product_id.scooters_ids
            customer_models_ids = self.browse(cr, uid, i, context).order_partner_id.scooters_id
            res[i] = comp(prod_models_ids, customer_models_ids)

        return res

    _inherit = 'sale.order.line'
    _columns = {
        'model_ok': fields.function(_get_customer_model,
                                    string='Compatible Product',
                                    type='boolean',
                                    method=True,
                                    help='Is the product compatible with the models in customer form ?'),
    }


sale_order_line()
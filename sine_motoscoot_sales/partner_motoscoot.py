# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
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

from osv import fields, osv


def _get_sale_products(self, cr, uid, ids, field_name, arg, context=None):
    res = {}
    sale_order_line_obj = self.pool.get('sale.order.line')
    for id in ids:
        sub_res = []
        sale_order_line_ids = sale_order_line_obj.search(cr, uid, [('order_partner_id', '=', id)])
    for sale_order_line_id in sale_order_line_ids:
        product_id = sale_order_line_obj.browse(cr, uid, sale_order_line_id, context=context).product_id.id
        sub_res.append(product_id)
        res[id] = sub_res
    return res


class res_partner(osv.osv):


    _inherit = 'res.partner'
    _columns = {
        'ventas': fields.function(_get_sale_products, type='one2many', obj='product.product', method=True, string='Ventas'),
        'category_id': fields.many2many('res.partner.category', id1='partner_id', id2='category_id', string='Tags'),
    }

    def onchange_partner_category(self, cr, uid, ids, part, context=None):

        for part in self.browse(cr, uid, ids, context=None):

            part_category = part.category_id.name
            val = {}
            pricelist = self.pool.get('product.pricelist').search(cr, uid, [('part_category', 'ilike', 'name')],
                                                              context=context)
            if part_category:
                val['property_product_pricelist'] = pricelist
                print val
                return {'value': val}


res_partner()


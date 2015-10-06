##############################################################################
#
#    OpenERP, Open Source Management Solution
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

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'stock_grn': fields.related('product_id','stock_grn', type='float', string='G'),
        'stock_bcn': fields.related('product_id','stock_bcn', type='float',  string='B'),
        'stock_pt': fields.related('product_id','stock_pt', type='float',  string='P'),
        'date_ordered': fields.related('order_id', 'date_order', type='char', relation='sale.order', string='Fecha Orden'),

    }

sale_order_line()


class sale_order(osv.osv):

    def partner_history(self, cr, uid, ids, context=None):
        partner_id = self.read(cr, uid, ids, 'partner_id')
        field_name = 'sale_id'
        sales_obj = self.pool['sale.order']
        sale_ids = sales_obj.browse(cr, uid, partner_id, context)
        sales_read = sales_obj.read(
            cr, uid, sale_ids, [field_name], context=context)
        return sales_read[field_name]


    _inherit = 'sale.order'
    _columns = {
        'sale_internal_comment':  fields.text('Internal Comment', help=''),

    }
sale_order()




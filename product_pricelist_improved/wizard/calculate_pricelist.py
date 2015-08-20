# -*- encoding: utf-8 -*-
##############################################################################
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2015 OBERTIX FREE SOLUTIONS (<http://obetix.net>).
#                       cubells <vicent@vcubells.net>
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class CalculatePricelist(orm.TransientModel):
    _name = "calculate.pricelist"
    _description = "Calculate Pricelist"

    _columns = {
        'pricelist_ids': fields.one2many('calculate.pricelist.line',
                                         'wizard_id', 'Pricelist line'),
        'state': fields.selection([
            ('initial', 'Initial'),
            ('done', 'Done'),
        ], 'State', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Customer', select=True),
        'product_id': fields.many2one('product.product', 'Product',
                                      domain=[('sale_ok', '=', True)],
                                      required=True),
        'qty': fields.integer('Quantity', required=True),
    }

    _defaults = {
        'state': lambda *a: 'initial',
        'qty': 1.0,
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        model = context.get('active_model', False)
        product_id = False
        if model and model == 'product.product':
            product_id = context.get('active_id')
        res = super(CalculatePricelist, self).default_get(cr, uid, fields,
                                                          context)
        if product_id and 'product_id' in fields:
            res['product_id'] = product_id
        return res

    def button_calculate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'done'})
        pricelist_obj = self.pool['product.pricelist']
        line_obj = self.pool['calculate.pricelist.line']
        line_ids = line_obj.search(cr, uid, [('wizard_id', 'in', ids)],
                                   context=context)
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            line_obj.unlink(cr, uid, line.id, context=context)
        data = self.browse(cr, uid, ids[0], context)
        price_ids = pricelist_obj.search(cr, uid, [('type', '=', 'sale')],
                                         context=context)
        for plist in pricelist_obj.browse(cr, uid, price_ids, context=context):
            price = pricelist_obj.price_get(
                cr, uid, [plist.id], data.product_id.id, data.qty,
                data.partner_id and data.partner_id.id or False,
                context=context)[plist.id]
            standard_price = data.product_id.standard_price or 0.0
            values = {
                'wizard_id': ids[0],
                'pricelist_id': plist.id,
                'product_id': data.product_id.id,
                'qty': float(data.qty),
                'price': price,
                'standard_price': standard_price,
                'margin': price - standard_price,
            }
            line_obj.create(cr, uid, values,context=context)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calculate.pricelist',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }


class CalculatePricelistLine(orm.TransientModel):
    _name = "calculate.pricelist.line"

    _columns = {
        'wizard_id': fields.many2one('calculate.pricelist', 'Wizard',
                                     readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist',
                                        readonly=True),
        'product_id': fields.many2one('product.product', 'Product',
                                      readonly=True),
        'qty': fields.integer('Quantity', readonly=True),
        'price': fields.float('Price', readonly=True),
        'standard_price': fields.float('Standard Price', readonly=True),
        'margin': fields.float('Margin', readonly=True),
    }


# -*- encoding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2013 Rafael Valle Sancho (<http://www.rvalle.es>). All Rights Reserved
# d$
#
# Enhanced by Sinergia Informatica 2015. David Hernández-
# Add product brand
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import osv
from osv import fields
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc
import logging

_logger = logging.getLogger(__name__)


class stock_rules(osv.osv):
    _name = 'stock.rules'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'category_id': fields.many2one('product.category', 'Product category',
                                       help="leave blank to apply to all products"),
        'stock_warehouse_orderpoint_id': fields.one2many('stock.warehouse.orderpoint', 'stock_rule_id',
                                                         'Warehouse orderpoint'),
        'min_amount': fields.integer('Min.Amount'),
        'max_amount': fields.integer('Max.Amount'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
        'location_id': fields.many2one('stock.location', 'Location'),
        'child_categories': fields.boolean('Include child categories'),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'Rules State', readonly=True, select=True),
        'brand_id': fields.many2one('product.brand', 'Brand', help="Marca sobre la que aplicar la regla"),
    }

    _defaults = {

        'state': 'draft',

    }

    def change_warehouse(self, cr, uid, ids, warehouse_id):
        if warehouse_id:
            warehouse_obj = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
            return {'value': {'location_id': warehouse_obj.lot_input_id.id}}

    def change_provider(self, cr, uid, ids, prov_id):
        if prov_id:
            prov_obj = self.pool.get('res.partner').browse(cr, uid, prov_id, ['supplier', 'is', True])
            return {'value': {'prov_id': prov_obj.id}}

    def change_brand(self, cr, uid, ids, brand_id):
        if brand_id:
            brand_obj = self.pool.get('product.brand').browse(cr, uid, brand_id)
            return {'value': {'brand_id': brand_obj.id}}

    def get_childs_categs(self, cr, uid, ids, parent_category_obj, childs_ids, context):

        childs_ids.append(parent_category_obj.id)

        if parent_category_obj.child_id:

            for child_obj in parent_category_obj.child_id:
                childs_ids.append(child_obj.id)

                self.get_childs_categs(cr, uid, ids, child_obj, childs_ids, context)

        return childs_ids

    def generate_rules(self, cr, uid, ids, context=None):

        stock_rules_obj = self.pool.get('stock.rules').browse(cr, uid, ids[0])

        # if assign category
        if stock_rules_obj.category_id:

            #not include childs categ
            if stock_rules_obj.child_categories == False:

                products_ids = self.pool.get('product.product').search(cr, uid, [('type', '=', 'product'),
                                                                                 ('procure_method', '=',
                                                                                  'make_to_stock'),
                                                                                 ('categ_id', '=',
                                                                                  stock_rules_obj.category_id.id),
                                                                                 ('product_brand_id', '=',
                                                                                  stock_rules_obj.brand_id.id),
                                                                                 ('active', '=', 1)])


                if products_ids:
                    for product_id in products_ids:
                        product_obj = self.pool.get('product.product').browse(cr, uid, product_id)

                        vals = {
                            'name': stock_rules_obj.name,
                            'product_id': product_obj.id,
                            'product_max_qty': stock_rules_obj.max_amount,
                            'product_min_qty': stock_rules_obj.min_amount,
                            'product_uom': product_obj.uom_id.id,
                            'warehouse_id': stock_rules_obj.warehouse_id.id,
                            'location_id': stock_rules_obj.location_id.id,
                            'stock_rule_id': stock_rules_obj.id
                        }

                        self.pool.get('stock.warehouse.orderpoint').create(cr, uid, vals)

                    stock_rules_obj.write({'state': 'done'})

            else:

                parent_category_obj = self.pool.get('product.category').browse(cr, uid, stock_rules_obj.category_id.id)

                childs_ids = []

                childs = self.get_childs_categs(cr, uid, ids, parent_category_obj, childs_ids, context)

                products_ids = self.pool.get('product.product').search(cr, uid, [('type', '=', 'product'), (
                    'procure_method', '=', 'make_to_stock'), ('categ_id', 'in', childs), ('product_brand_id', '=',
                                                                                          stock_rules_obj.brand_id.id),
                                                                                         ('active', '=', 1)])

                if products_ids:
                    for product_id in products_ids:
                        product_obj = self.pool.get('product.product').browse(cr, uid, product_id)

                        vals = {
                            'name': stock_rules_obj.name,
                            'product_id': product_obj.id,
                            'product_max_qty': stock_rules_obj.max_amount,
                            'product_min_qty': stock_rules_obj.min_amount,
                            'product_uom': product_obj.uom_id.id,
                            'warehouse_id': stock_rules_obj.warehouse_id.id,
                            'location_id': stock_rules_obj.location_id.id,
                            'stock_rule_id': stock_rules_obj.id
                        }

                        self.pool.get('stock.warehouse.orderpoint').create(cr, uid, vals)
                    stock_rules_obj.write({'state': 'done'})

                    # if not category
        else:

            products_ids = self.pool.get('product.product').search(cr, uid, [('type', '=', 'product'),
                                                                             ('procure_method', '=', 'make_to_stock'),
                                                                             ('product_brand_id', '=',
                                                                              stock_rules_obj.brand_id.id),
                                                                             ('active', '=', 1)])

            if products_ids:
                for product_id in products_ids:
                    product_obj = self.pool.get('product.product').browse(cr, uid, product_id)

                    vals = {
                        'name': stock_rules_obj.name,
                        'product_id': product_obj.id,
                        'product_max_qty': stock_rules_obj.max_amount,
                        'product_min_qty': stock_rules_obj.min_amount,
                        'product_uom': product_obj.uom_id.id,
                        'warehouse_id': stock_rules_obj.warehouse_id.id,
                        'location_id': stock_rules_obj.location_id.id,
                        'stock_rule_id': stock_rules_obj.id
                    }

                    self.pool.get('stock.warehouse.orderpoint').create(cr, uid, vals)

                    stock_rules_obj.write({'state': 'done'})

        return True


    def update_rules(self, cr, uid, ids, context=None):

        stock_rules_obj = self.pool.get('stock.rules').browse(cr, uid, ids[0])

        for rules_obj in stock_rules_obj.stock_warehouse_orderpoint_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, rules_obj.product_id.id)

            vals = {
                'name': stock_rules_obj.name,
                'product_max_qty': stock_rules_obj.max_amount,
                'product_min_qty': stock_rules_obj.min_amount,
                'warehouse_id': stock_rules_obj.warehouse_id.id,
                'location_id': stock_rules_obj.location_id.id,
                'stock_rule_id': stock_rules_obj.id
            }

            self.pool.get('stock.warehouse.orderpoint').write(cr, uid, rules_obj.id, vals)

        return True


    def drop_rules(self, cr, uid, ids, context=None):

        stock_rules_obj = self.pool.get('stock.rules').browse(cr, uid, ids[0])

        rules_ids = []
        for rules_obj in stock_rules_obj.stock_warehouse_orderpoint_id:
            rules_ids.append(rules_obj.id)

        self.pool.get('stock.warehouse.orderpoint').unlink(cr, uid, rules_ids)
        stock_rules_obj.write({'state': 'cancel'})

        return True


stock_rules()


class stock_warehouse_orderpoint(osv.osv):
    _name = 'stock.warehouse.orderpoint'
    _inherit = 'stock.warehouse.orderpoint'

    _columns = {

        'stock_rule_id': fields.many2one('stock.rules', 'Stock rule'),

    }


stock_warehouse_orderpoint()



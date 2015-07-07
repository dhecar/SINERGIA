# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv import fields, osv


class product_brand(osv.osv):
    _name = "product.brand"
    _inherit = 'product.brand'
    _description = 'Discount gived by Manufacturer'
    _columns = {
        'brand_discount': fields.float('Discount',
                                       digits_compute=dp.get_precision('Discount offered by the manufacturer')),
    }


product_brand()


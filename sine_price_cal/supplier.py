# -*- coding: utf-8 -*-

##############################################################################
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _



class product_supplierinfo(osv.osv):

    _name = "product.supplierinfo"
    _inherit = 'product.supplierinfo'




    _columns = {

        'supplier_discount':fields.float('Descuento del Proveedor', required=False, help="Descuento proporcionado por el Proveedor"),

    }

product_supplierinfo()

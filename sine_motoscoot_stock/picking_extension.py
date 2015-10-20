from osv import fields, osv
import one2many_sorted


class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'is_printed': fields.boolean('Is printed?', help='Is the picking printed?'),
        'payment1_id': fields.related('sale_id', 'payment_type', type='many2one', relation='payment.type',
                                      string='Tipo Pago Magento', readonly=True),
        'payment2_id': fields.related('sale_id', 'payment_method_id', type='many2one', relation='payment.method',
                                      string='Tipo Pago Erp', readonly=True),
        'sh_id': fields.related('sale_id', 'shop_id', type='many2one', relation='sale.shop',
                                string='Tienda', readonly=True),
        'pricelist_type': fields.related('sale_id', 'pricelist_id', type='many2one', relation='product.pricelist',
                                         string='Tarifa', readonly=True),

        'move_lines_sorted': one2many_sorted.one2many_sorted
        ('stock.move'
         , 'picking_id'
         , 'Moves Sorted'
         , states={'draft': [('readonly', False)]}
         , order='product_id.product_brand_id.name, product_id.default_code'
         )

    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_lines_sorted': []})
        return super(stock_picking_out, self).copy(cr, uid, id, default, context=context)


class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _columns = {

        'move_lines_sorted': one2many_sorted.one2many_sorted
        ('stock.move'
         , 'picking_id'
         , 'Moves Sorted'
         , states={'draft': [('readonly', False)]}
         , order='product_id.product_brand_id.name, product_id.default_code'
         )
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_lines_sorted': []})
        return super(stock_picking_in, self).copy(cr, uid, id, default, context=context)


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'is_printed': fields.boolean('Is printed?', help='Is the picking printed?'),
        'payment1_id': fields.related('sale_id', 'payment_type', type='many2one', relation='payment.type',
                                      string='Tipo Pago Magento', readonly=True),
        'payment2_id': fields.related('sale_id', 'payment_method_id', type='many2one', relation='payment.method',
                                      string='Tipo Pago Erp ', readonly=True),
        'sh_id': fields.related('sale_id', 'shop_id', type='many2one', relation='sale.shop',
                                string='Tienda', readonly=True),
        'pricelist_type': fields.related('sale_id', 'pricelist_id', type='many2one', relation='product.pricelist',
                                         string='Tarifa', readonly=True),
        'move_lines_sorted': one2many_sorted.one2many_sorted
        ('stock.move'
         , 'picking_id'
         , 'Moves Sorted'
         , states={'draft': [('readonly', False)]}
         , order='product_id.product_brand_id.name, product_id.default_code'
         )
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_lines_sorted': []})
        return super(stock_picking, self).copy(cr, uid, id, default, context=context)


class stock_move(osv.osv):

    _inherit = 'stock.move'
    _columns = {

        'stock_grn': fields.related('product_id', 'stock_grn', type='float', string='G'),
        'stock_bcn': fields.related('product_id', 'stock_bcn', type='float',  string='B'),
        'stock_pt': fields.related('product_id', 'stock_pt', type='float',  string='P'),

    }
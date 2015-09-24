from osv import fields, osv



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
    }


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

    }
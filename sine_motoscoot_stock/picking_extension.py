from osv import fields, osv


class stock_picking_out(osv.osv):

    _inherit = "stock.picking.out"
    _columns = {
        'is_printed': fields.boolean('Is printed?', help='Is the picking printed?'),
    }


class stock_picking(osv.osv):

    _inherit = "stock.picking"
    _columns = {
        'is_printed': fields.boolean('Is printed?', help='Is the picking printed?'),
    }
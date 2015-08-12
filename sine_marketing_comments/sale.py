# -*- coding: utf-8 -*-
# David Hernández. http://sinergiainformatica.net
#
# ##################################################

from openerp.osv import orm, fields, osv


class sale_order(orm.Model):
    _inherit = "sale.order"
    _columns = {
        'comment_id': fields.many2one('sale.comment',
                                      'Comment for the order',
                                      ondelete='restrict')
    }
sale_order()


class sale_comment(orm.Model):
    _name = "sale.comment"
    _description = "Add a comment for the sales orders"
    _table = "sale_comment"
    _rec_name = "comment"
    _columns = {

        'comment': fields.char('Comment',
                               help="Comment for sales",
                               required=True, size=120),
    }
sale_comment()

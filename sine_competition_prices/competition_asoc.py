import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv import fields, osv


class competition_asoc(osv.osv):
    _name = 'competition.asoc'
    _descripcion = 'Asociated product URL'
    _rec_name = 'linked_to'

    _columns = {
        'asoc': fields.many2one('product.product', 'asoc_id'),
        'web_product': fields.char('Url ', size=150),
        'linked_to': fields.many2one('competition.url', 'Related web', required=True, help="Web page "),
        'online_price': fields.char('Online Price', size=6),


    }


competition_asoc()


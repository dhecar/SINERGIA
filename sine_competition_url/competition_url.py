import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv import fields, osv

import urllib
import re


class competition_url(osv.osv):
    _name = 'competition.url'
    _description = 'URL for competition'
    _table = 'competition_url'
    _rec_name = 'url_competition'
    _columns = {
        'url_competition': fields.char('Url ', size=150),
        'regex': fields.char('Expression', size=300),
    }


competition_url()


# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp.addons.connector.unit.mapper import (mapping, ImportMapper)
from .backend import magento_myversion


@magento_myversion
class MySaleOrderImportMapper(ImportMapper):
    _inherit = 'magento.sale.order'
    _columns = {
        'warehouse': fields.char('Magento warehouse', size=1)
    }

    #direct = ImportMapper.direct + [('assignation', 'warehouse')]
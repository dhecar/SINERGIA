# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Guewen Baconnier
# Copyright 2012 Camptocamp SA

# Adaptation to ASM by David Hernández
# http://sinergiainformatica.net
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import openerp.addons.decimal_precision as dp


class carrier_file(osv.osv):
    _inherit = 'delivery.carrier.file'


    def _get_reembolso(self, cursor, user_id, context=None):
        return (
            ('P', 'Portes Pagados'),
            ('D', 'Portes debidos'),
            ('A', 'Ambos'),
            )

    def _get_typo(self, cursor, user_id, context=None):
        return (
            ('54', 'EURO STANDARD'),
            ('37', 'ECONOMY'))


    def get_type_selection(self, cr, uid, context=None):
        result = super(carrier_file, self).get_type_selection(cr, uid, context=context)
        if 'ASM' not in result:
            result.append(('ASM', 'Envíos ASM'))
        return result

    _columns = {
        'type': fields.selection(get_type_selection, 'Type', required=True),
        'asm_account': fields.char('Agent Account', size=9),
        'asm_typo': fields.selection(_get_typo, 'Tipo de servicio'),
        'asm_portes': fields.selection(_get_reembolso, 'Tipo de portes'),
        'asm_cod_price': fields.float('Precio contrareembolso',
                                        digits_compute=dp.get_precision('Precio de reembolso')),
        'PlzOrg': fields.integer('Lugar de recogida', size=3),

    }


carrier_file()

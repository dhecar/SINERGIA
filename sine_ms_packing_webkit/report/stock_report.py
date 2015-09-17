# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (c) 2011-2013 Camptocamp SA (http://www.camptocamp.com)
#   @author Nicolas Bessi
#   Copyright (c) 2013 Agile Business Group (http://www.agilebg.com)
#   @author Lorenzo Battistini
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from report import report_sxw
from osv import fields, osv
import time


class DeliverySlip(report_sxw.rml_parse):

    def _get_invoice_address(self, picking):
        if picking.sale_id:
            return picking.sale_id.partner_invoice_id
        partner_obj = self.pool.get('res.partner')
        invoice_address_id = picking.partner_id.address_get(
            adr_pref=['invoice']
        )['invoice']
        return partner_obj.browse(
            self.cr, self.uid, invoice_address_id)

    def _get_shipping_address(self, picking):
        if picking.sale_id:
            return picking.sale_id.partner_shipping_id
        partner_obj = self.pool.get('res.partner')
        shipping_address_id = picking.partner_id.address_get(
            adr_pref=['shipping']
        )['shipping']
        return partner_obj.browse(
            self.cr, self.uid, shipping_address_id)


    def __init__(self, cr, uid, name, context):
        super(DeliverySlip, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'invoice_address': self._get_invoice_address,
            'shipping_address': self._get_shipping_address,
        })


report_sxw.report_sxw('report.webkit.motoscoot_picking',
                      'stock.picking',
                      'addons/sine_ms_packing_webkit/report/delivery_slip.mako',
                      parser=DeliverySlip)

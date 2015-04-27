# -*- coding: utf-8 -*-
##############################################################################
#
# Author: David Hernandez
#    Sinergiainformatica.net
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
import logging
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from openerp.addons.connector_ecommerce.sale import (ShippingLineBuilder,
                                                     CashOnDeliveryLineBuilder,
                                                     GiftOrderLineBuilder)
_logger = logging.getLogger(__name__)


class SaleOrderImportMapperExtension(ImportMapper):
    _inherit = 'magento.sale.order'

    def _add_cash_on_delivery_line_extension(self, map_record, values):
        record = map_record.source
        amount_excl = float(record.get('msp_base_cashondelivery') or 0.0)
        amount_incl = float(record.get('msp_base_cashondelivery_incl_tax') or 0.0)
        if not (amount_excl or amount_incl):
            return values
        line_builder = self.get_connector_unit_for_model(
            MagentoCashOnDeliveryLineBuilder)
        tax_include = self.options.tax_include
        line_builder.price_unit = amount_incl if tax_include else amount_excl
        line = (0, 0, line_builder.get_line())
        values['order_line'].append(line)
        return values



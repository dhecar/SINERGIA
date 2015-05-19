# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
#
# Adaptation to ASM
# Author: David Hernandez
#    http://sinergiainformatica.net
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
import csv

from openerp.addons.base_delivery_carrier_files.generator import CarrierFileGenerator
from openerp.addons.base_delivery_carrier_files.generator import BaseLine
from openerp.addons.base_delivery_carrier_files.csv_writer import UnicodeWriter


class AsmLine(BaseLine):
    fields = (('TipoRegistro', 1),
              ('PlzOrg', 3),
              ('NomRemitente', 40),
              ('DirecRemitente', 40),
              ('PoblRemitente', 40),
              ('CodPaisRemitente', 4),
              ('CodPostalRemitente', 5),
              ('FechaExpedicion', 10),
              ('CodPlazaCliente', 3),
              ('CodCliente', 6),
              ('TipoPortes', 1),
              ('Referencia', 15),
              ('name', 80),
              ('street', 80),
              ('state', 40),
              ('city', 4),
              ('zip', 15),
              ('asm_typo', 2),
              ('horario_servicio', 3),
              ('Bultos', 4),
              ('weight', 6),
              ('CodAgente', 5),
              ('TipoReferencia', 1))

class AsmFileGenerator(CarrierFileGenerator):
    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'ASM'

    def _get_filename_single(self, picking, configuration, extension='csv'):
        return super(AsmFileGenerator, self)._get_filename_single(picking, configuration, extension='csv')

    def _get_filename_grouped(self, configuration, extension='csv'):
        return super(AsmFileGenerator, self)._get_filename_grouped(configuration, extension='csv')

    def _get_rows(self, picking, configuration):
        """
        Returns the rows to create in the file for a picking

        :param browse_record picking: the picking for which we generate a row in the file
        :param browse_record configuration: configuration of the file to generate
        :return: list of rows
        """
        line = AsmLine()
        line.TipoRegistro = '1'
        line.PlzOrg = configuration.PlzOrg
        address = picking.partner_id
        if address:
            line.name = address.name or (address.partner_id and address.partner_id.name)
            line.street = address.street
            line.city = address.city
            line.state = address.state_id.name
            line.zip = address.zip
            line.phone = address.phone or address.mobile
            line.nif = "nif"
            line.asm_cod_price = configuration.asm_cod_price
            line.CodPaisRemitente= "34"
        company = picking.sale_id.company_id
        if company:
            line.NomRemitente = company.name
            line.DirecRemitente = company.street
            line.PoblRemitente = company.state_id.name
            line.CodPaisRemitente = "54"
            line.CodPostalRemitente = company.zip
            line.CodPlazaCliente = '332'

        line.FechaExpedicion = picking.date
        line.Referencia = picking.name
        line.asm_typo = configuration.asm_typo
        line.TipoPortes= configuration.asm_portes
        line.weight = "%.2f" % (picking.weight,)
        line.mail = address.email

        return [line.get_fields()]



    def _write_rows(self, file_handle, rows, configuration):
        """
        Write the rows in the file (file_handle)

        :param StringIO file_handle: file to write in
        :param rows: rows to write in the file
        :param browse_record configuration: configuration of the file to
               generate
        :return: the file_handle as StringIO with the rows written in it
        """

        writer = UnicodeWriter(file_handle, delimiter='|', quotechar='"',
                               lineterminator='\n', quoting=csv.QUOTE_NONE)
        writer.writerows(rows)
        return file_handle

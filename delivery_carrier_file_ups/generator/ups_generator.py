# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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


class UPSLine(BaseLine):
    fields = (('name', 30),
              ('name', 30),
              ('street', 30),
              ('city', 30),
	      ('country',2),
              ('zip', 9),
	      ('phone',16),
	      ('mail', 50),
	      ('mail', 50),
	      ('ups_account',9),
	      ('service',2),
	      ('package_type',2),
	      ('numpack',2),
	      ('weight',3),
	      ('goods',15),
	      ('reference1',20),
	      ('reference2',20),
	      ('cash',1),
	      ('ups_cod_price',3),
	      ('amount',4),
	      ('currency',1),
	      ('total'))


class UpsFileGenerator(CarrierFileGenerator):

    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'Ups'

    def _get_filename_single(self, picking, configuration, extension='csv'):
        return super(UpsFileGenerator, self)._get_filename_single(picking, configuration, extension='csv')

    def _get_filename_grouped(self, configuration, extension='csv'):
        return super(UpsFileGenerator, self)._get_filename_grouped(configuration, extension='csv')

    def _get_rows(self, picking, configuration):
        """
        Returns the rows to create in the file for a picking

        :param browse_record picking: the picking for which we generate a row in the file
        :param browse_record configuration: configuration of the file to generate
        :return: list of rows
        """
        line = UPSLine()
	line.reference = picking.name
        address = picking.partner_id
        if address:
            line.name = address.name or (address.partner_id and address.partner_id.name)
            # if a company, put company name
            #if address.street.partner_id.title:
            #    line.company_name = address.partner_id.name
            line.street = address.street
            line.zip = address.zip
            line.city = (address.city and address.state_id.name)
            line.country = address.country_id.code
            line.phone = address.phone or address.mobile
            line.mail = address.email
	line.ups_account = configuration.ups_account
	line.service = configuration.ups_service_level
	line.package_type = configuration.ups_package_type
	line.numpack = picking.number_of_packages
        line.goods = configuration.ups_description_goods
	line.reference1 = picking.name
	line.reference2 = picking.name
	#line.amount = picking.origin.amount
	#line.currency = picking.origin.currency
	line.weight = "%.2f" % (picking.weight)
	line.cash = configuration.ups_cash
	line.ups_cod_price = configuration.ups_cod_price
	line.total = picking.sale_id.amount_total
	line.currency = picking.company_id.currency_id.name
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
        writer = UnicodeWriter(file_handle, delimiter=';', quotechar='"',
                               lineterminator='\n', quoting=csv.QUOTE_NONE)
        writer.writerows(rows)


	return file_handle




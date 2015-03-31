# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import fields,osv


import psycopg2
import sys
import csv
from decimal import Decimal
from collections import defaultdict
import os
import paramiko

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time


class scooter_asociaciones(osv.osv):
    _name = 'scooter.asociaciones'
    _descripcion = 'Listado de Asociaciones'
    _table = 'scooter_asociaciones'
    _rec_name ='model_id'
    _columns = {
        'type': fields.selection((('SCOOT','Scooters 50cc'),('SCOOT2','Scooter 100-600cc'),('MARCH2','Marchas 125cc'),('PBKE', 'PitBike 4T'),('MARCH','Marchas 50cc-80cc'),('VESP','Vespas-Clasicas 50cc-200cc'),('MXSC','Maxiscooter'),('PBIKE','PocketBike')),'Selecciona tipo',required=False),
        'brand_id': fields.many2one('marcas.scooter', 'Marca', required=False, readonly=False),
        'model_id': fields.many2one('scooter.model', 'Modelo', required=False,readonly=False),
        'compatible_with_ids': fields.many2many('product.product', 'scooter_compat_with_product_rel', 'scooter_id', 'product_id', string="Compatible con"),
}

scooter_asociaciones()







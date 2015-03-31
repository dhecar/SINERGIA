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


class vehicle_config(osv.osv):
    _name = 'vehicle.config'
    _descripcion = 'Configuration for Vehicle Fits link'
    _table = 'vehiclefits_config'
    _columns = {
    
	'name': fields.char('Name',size=20),
	'vf_url':fields.char('Url',size=30,help="Url to Magento Web"),
	'db_user':fields.char('DB user',size=20,required=True),
	'db_password':fields.char('DB password', size=20,required=True),
	'db_host' : fields.char ('IP DB host', size=15,required=True),
	'db_name' : fields.char ('DB name', size=30,required=True),
}

vehicle_config()




class vehicle_export(osv.osv):
    _name ='vehicle.export'
    _description = 'Export Vehicle Fits to Magento'
    _table = 'vehiclefits_export'

    _columns = {

	'date':fields.char('Last Export', size=20),
}

vehicle_export()







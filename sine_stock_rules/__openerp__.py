# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2013 Rafael Valle Sancho (<http://www.rvalle.es>). All Rights Reserved
#    d$
#
#   Enhanced by Sinergia Informatica 2015. David Hernández-
#   Add product brand
#
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
##############################################################################
{
    "name" : "stock_rules",
    "version" : "0.1",
    "author" : "Rafael Valle",
    "website": "http://www.rvalle.es",
    "description" : 
    """
    This is a small module development for do easily the task of create stock rules for products in openerp.

    -Allows create stock rules for category products

    -Allows create stock rules for product brand

    -Allows easily create, update and drop multiple stock rules

    -Only for stockable products and procured method is make to Stock

    * The menu is in Stock/Configuration/Stock Rule Generator

    *  Compatible with OpenERP 6.1 and OpenERP 7
    
     """,
    "category": "Generic Modules",
    "depends": ['base',
                 'product',
                 'sale',
                 'stock',
                 ],

    "init_xml": [],
    "update_xml": [
        'stock_rules_view.xml'
        ],
    'installable': True,
    'active': False,  
}

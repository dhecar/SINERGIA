# -*- coding: utf-8 -*-
{
    "name": "Vehicle Fits Module for Openerp",
    "version": "7.0",
    "author": "David Hernández",
    "category": "Generic Modules/Others",
    "website": "http://sinergiainformatica.net",
    "description": "Export the applications for products to Vehicle Fits. http://vehiclefits.com/. You need a RSA key"
                   "to connect throught sftp to push the csv file",
    "depends": ["sine_scooter_models", "product"],
    "update_xml": ["vehicle_fits_view.xml"],
    "data": ['security/security.xml', 'security/ir.model.access.csv'],
    "active": True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

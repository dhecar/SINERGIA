# -*- coding: utf-8 -*-

##############################################################################
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_product(osv.osv):
    def get_pvp(self, cr, uid, ids, val, arg, context=None):
        supl_obj = self.pool.get('product.supplierinfo')
        supl_ids = supl_obj.search(cr, uid, [])
        supl_disc = supl_obj.read(cr, uid, supl_ids, ['discount_supplier'])
        for product in self.browse(cr, uid, ids, context=context):
            print supl_disc

            self.write(cr, uid, product.id, {'pvp': supl_disc[0]})


    _name = 'product.product'
    _inherit = 'product.product'


    ##################################
    disc = map(str, range(0, 61))
    _selection_vals = zip(disc, disc)

    _columns = {

        'pcoste': fields.float('Precio de Coste', digits_compute=dp.get_precision('Precio de coste del producto')),
        'list_price2': fields.float('PCM', digits_compute=dp.get_precision('Precio Catalogo Motoscoot')),
        'pvp_fabricante': fields.float('PVP Fabricante',
                                       digits_compute=dp.get_precision('Precio recomendado por fabricante')),
        'pvptt': fields.float('PVT', digits_compute=dp.get_precision('Precio de venta Toptaller')),
        'pvp_taller': fields.float('Precio Venta a Taller', digits_compute=dp.get_precision(
            'Precio de venta al Taller basado en el descuento por defecto')),
        'descuento': fields.float('Descuento por defecto',
                                  digits_compute=dp.get_precision('Descuento aplicado por defecto')),
        'precio_online': fields.float('Precio Online 5%', digits_compute=dp.get_precision('Precio Online Motoscoot')),
        'incremento_p_coste': fields.float('Incremento Precio Coste'),
        #
        'pvp': fields.float('PVP Fabricante', digits_compute=dp.get_precision('Precio recomendado por fabricante')),
        'pvpms': fields.float('PVP Toptaller',
                              digits_compute=dp.get_precision('Precio establecido basado en el coste')),
        'price2': fields.float('Precio Taller', digits_compute=dp.get_precision('Precio Taller')),
        'standard_price2': fields.float('Precio de Coste',
                                        digits_compute=dp.get_precision('Precio de coste del producto')),
        'desctaller': fields.selection(_selection_vals, 'Elije descuento', required=False),
        'descfabricante': fields.related('seller_ids', 'supplier_discount', type='float',
                                         string='Descuento del proveedor'),
        # 'descfabricante':fields.float('Descuento del Fabricante', digits_compute=dp.get_precision('Descuento de Fabricante a MS')),
        'beneficio': fields.float('Beneficio de la venta', digits_compute=dp.get_precision('Beneficio de la Venta')),
        'margen_beneficio': fields.float('Margen beneficio minimo',
                                         digits_compute=dp.get_precision('Margen de beneficio que queremos aplicar')),
        'p_online': fields.float('Precio Online 5%', digits_compute=dp.get_precision('Precio online 5%')),
        'precio_neto': fields.float('Neto', digits_compute=dp.get_precision('Neto')),
        'p_catalogo_ms': fields.float('PCM', digits_compute=dp.get_precision('PCM')),
        'basado_p_coste': fields.boolean("Basado en precio de coste?"),
        'p_catalogo_ms_neto': fields.float('PCM neto', digits_compute=dp.get_precision('PCM neto')),
        'competencia': fields.boolean("Precio menor de la competencia"),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        'partner_calc_price': fields.float('Precio para cliente',
                                           digits_compute=dp.get_precision('Precio para cliente')),

    }

    _defaults = {
        'desctaller': lambda *a: 0,
        'margen_beneficio': lambda *a: 20,
    }

    # ON_CHANGE PARTNER #

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        if pricelist:
            val = {
                'pricelist_id': pricelist
            }
        return {'value': val}

    #  CALCULO PRECIO SEGUN PARTNER ESCOGIDO

    def amount(self, cr, uid, ids, partner_calc_price, pricelist_id, partner_id, context=None):
        if not pricelist_id:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                         'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg + "\n\n"
        else:
            uom = False
            qty = 1.0
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], ids[0], qty, partner_id)[
                pricelist_id]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                             "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg + "\n\n"
            else:
                val = {
                    'partner_calc_price': price
                }
            return {'value': val}


    def desctaller_onchange(self, cr, uid, ids, desctaller, pvp, price2, basado_p_coste, standard_price2,
                            descfabricante, margen_beneficio, context=None):
        if context is None:
            context = context
        if basado_p_coste is True:
            min_benf = float(standard_price2) + (float(standard_price2) * (float(margen_beneficio) / 100.0))
            x = pvp - (pvp * (float(desctaller) / 100.0))

            if min_benf < x:
                val = {
                    'price2': x,
                }
                return {'value': val}
            else:
                res = {}
                warning = {
                    'title': _("Error"),
                    'message': _('Has superado el beneficio minimo establecido'),
                }
                return {'value': res.get('value', {}), 'warning': warning}

        else:
            if not pvp:
                res = {}
                warning = {
                    'title': _("Error"),
                    'message': _('Debes definir un PVP fabricante y un descuento'),
                }
                return {'value': res.get('value', {}), 'warning': warning}

            else:
                p_coste = float(pvp) - ( float(pvp) * float(descfabricante) / 100.0)
                min_benf = (p_coste + (p_coste * (margen_beneficio / 100.00)))
                y = float(pvp) - (float(pvp) * (float(desctaller) / 100.0))
                if min_benf < y:
                    val = {
                        'price2': y,

                    }
                    return {'value': val}
                else:
                    res = {}
                    warning = {
                        'title': _("Error"),
                        'message': _('Has superado el beneficio minimo establecido'),
                    }
                    return {'value': res.get('value', {}), 'warning': warning}


    def price2_onchange(self, cr, uid, ids, pvp, price2, basado_p_coste, standard_price2, descfabricante, context=None):

        if basado_p_coste is True:

            val = {
                'beneficio': ((float(price2) - float(standard_price2)) / (float(standard_price2))) * 100.00
            }
            return {'value': val}

        else:
            p_coste = float(pvp) - ( float(pvp) * float(descfabricante) / 100.0)
            p = ((float(price2) - float(p_coste)) / (float(p_coste))) * 100.00
            val = {
                'beneficio': ((float(price2) - float(p_coste)) / (float(p_coste))) * 100.00
            }
            return {'value': val}


    def pvp_basado_coste(self, cr, uid, ids, basado_p_coste, incremento_p_coste, pvp, standard_price2, context=None):

        pvp_iva = pvp + (pvp * 0.21)
        pvp_iva_5 = pvp_iva - (pvp_iva * 0.05)

        if basado_p_coste is False:
            val = {
                'pvpms': float(pvp),
                'precio_online': pvp_iva_5

            }
            return {'value': val}

        if basado_p_coste is True and standard_price2 <> 0:
            val = {
                'incremento_p_coste': ((float(pvp) - float(standard_price2)) / float(standard_price2)) * 100.00,
                'pvpms': pvp,
                'precio_online': pvp_iva_5

            }
            return {'value': val}
        else:
            res = {}
            warning = {
                'title': _("Error"),
                'message': _('Por favor introduce el precio de coste'),
            }
            return {'value': res.get('value', {}), 'warning': warning}


    def update_values(self, cr, uid, ids, context=None):
        for price in self.browse(cr, uid, ids, context=None):
            if price.basado_p_coste:
                self.write(cr, uid, ids, {
                    'pvp_fabricante': price.pvp,
                    'pcoste': price.standard_price2,
                    'pvptt': price.pvp,
                    'descuento': price.desctaller,
                    'pvp_taller': price.price2,
                    'p_online': price.precio_online,
                    'list_price2': price.p_catalogo_ms,
                    'list_price': price.p_catalogo_ms_neto,
                    'standard_price': price.standard_price2}, context=context)


            else:
                p_coste = float(price.pvp) - ( float(price.pvp) * float(price.descfabricante) / 100.0)
                self.write(cr, uid, ids, {
                    'pvp_fabricante': price.pvp,
                    'pcoste': p_coste,
                    'pvptt': price.pvp,
                    'descuento': price.desctaller,
                    'pvp_taller': price.price2,
                    'p_online': price.precio_online,
                    'list_price2': price.p_catalogo_ms,
                    'list_price': price.p_catalogo_ms_neto,
                    'standard_price': p_coste}, context=context)

    def price_catalog(self, cr, uid, ids, p_catalogo_ms, precio_online, context=None):
        val = {
            'p_catalogo_ms': float(precio_online) / 0.95,
            'precio_neto': float(precio_online) / 1.21,
        }
        return {'value': val}

    def catalogo_neto(self, cr, uid, ids, p_catalogo_ms, context=None):
        val = {
            'p_catalogo_ms_neto': float(p_catalogo_ms) / 1.21,
        }
        return {'value': val}


    def desc_onchange(self, cr, uid, ids, descfabricante, context=None):
        val = {
            'seller_ids.supplier_discount': descfabricante,
        }

        return {'value': val}


product_product()



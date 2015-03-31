# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv import fields, osv
import htmlmin
import urllib2
import re




class product_product(osv.osv):
    def get_prices(self,cr,uid,ids,context=None):
	asoc_obj = self.pool.get('competition.asoc')
	for product in self.browse(cr, uid, ids, context=context):
	    for asoc in product.asoc_id:
		res= {}
		web = asoc.web_product
		regex = asoc.linked_to.regex
		url = asoc.linked_to.url_competition
		htmlfile = urllib2.urlopen(web)
		html = htmlfile.read()
		htmlencoded = html.decode('iso8859-1')
		htmltext = htmlmin.minify(htmlencoded,remove_comments=True, remove_empty_space=True, remove_all_empty_space=False, reduce_empty_attributes=True, reduce_boolean_attributes=True, remove_optional_attribute_quotes=False, keep_pre=False, pre_tags=(u'pre', u'textarea'), pre_attr='pre')
		pattern = re.compile (regex)
		price = re.findall(pattern,htmltext)
		print htmltext
		print price
		
		asoc_obj.write(cr, uid,asoc.id,{'online_price':price[0]}, context=context)


    _name ='product.product'
    _inherit ='product.product'
    _descripcion = 'Asociated product URL'


    _columns = {
	'asoc_id': fields.one2many('competition.asoc','asoc'),
}

product_product()




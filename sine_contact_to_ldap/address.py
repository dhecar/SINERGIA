# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010-2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Nicolas Bessi (Camptocamp), Thanks to Laurent Lauden for his code adaptation
# Active directory Donor: M. Benadiba (Informatique Assistances.fr)
# Contribution : Joel Grand-Guillaume
#
# Adapted to fill MyPBXu100 LDAP server by Sinergiainformatica.net
# Author:David Hernandez. 2015
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
# TODO FInd why company parameter are cached
import re
import unicodedata
import netsvc

try:
    import ldap
    import ldap.modlist
except:
    print 'python ldap not installed please install it in order to use this module'

from osv import osv, fields
from tools.translate import _

logger = netsvc.Logger()


class LdapConnMApper(object):
    """LdapConnMApper: push specific fields from the Erp Partner to the
        LDAP schema inetOrgPerson. Ldap bind options are stored in company.r"""

    def __init__(self, cursor, uid, osv_obj, context=None):
        """Initialize connexion to ldap by using parameter set in the current user compagny"""
        logger.notifyChannel("MY TOPIC", netsvc.LOG_DEBUG,
                             _('Initalize LDAP CONN'))
        self.USER_DN = ''
        self.CONTACT_DN = ''
        self.LDAP_SERVER = ''
        self.PASS = ''
        self.OU = ''
        self.connexion = ''
        self.ACTIVDIR = False

        # Reading ldap pref
        user = osv_obj.pool.get('res.users').browse(cursor, uid, uid, context=context)
        company = osv_obj.pool.get('res.company').browse(cursor,
                                                         uid,
                                                         user.company_id.id,
                                                         context=context)
        self.USER_DN = company.base_dn
        self.CONTACT_DN = company.contact_dn
        self.LDAP_SERVER = company.ldap_server
        self.PASS = company.passwd
        self.PORT = company.ldap_port
        self.OU = company.ounit
        self.ACTIVDIR = company.is_activedir

        mand = (self.USER_DN, self.CONTACT_DN, self.LDAP_SERVER, self.PASS, self.OU)

        if company.ldap_active:
            for param in mand:
                if not param:
                    raise osv.except_osv(_('Warning !'),
                                         _('An LDAP parameter is missing for company %s') % (company.name,))

    def get_connexion(self):
        """create a new ldap connexion"""
        logger.notifyChannel("LDAP Address", netsvc.LOG_DEBUG,
                             _('connecting to server ldap %s') % (self.LDAP_SERVER,))

        username = "%s,%s" % (self.USER_DN, self.CONTACT_DN)
        password = "%s" % self.PASS

        if self.PORT:
            self.connexion = ldap.set_option(ldap.VERSION, ldap.VERSION3)
            self.connexion = ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            self.connexion = ldap.initialize('ldap://%s:%d' % (self.LDAP_SERVER,
                                                               self.PORT))
            self.connexion.simple_bind(username, password)

        else:
            self.connexion = ldap.set_option(ldap.VERSION, ldap.VERSION3)
            self.connexion = ldap.initialize('ldap://%s:%d' % self.LDAP_SERVER)
            self.connexion.simple_bind(self.USER_DN, self.CONTACT_DN, self.PASS)
        return self.connexion


class LDAPAddress(osv.osv):
    """Override the CRUD of the objet in order to dynamically bind to ldap"""
    _inherit = 'res.partner'
    ldapMapper = None

    def _name_get_fnc(self, cr, uid, ids, field_name, arg, context):
        x = {}
        for record in self.browse(cr, uid, ids, context):
            fullname = record.name
            a = fullname.split(' ', 1)[0]
            b = fullname.split()[-1]
            x[record.id] = a + " " + b
        return x

    _columns = {

    }

    def create(self, cursor, uid, vals, context={}):
        self.getconn(cursor, uid, {})
        ids = None
        self.validate_entries(vals, cursor, uid, ids)
        tmp_id = super(LDAPAddress, self).create(cursor, uid,
                                                 vals, context)
        if self.ldaplinkactive(cursor, uid, context):
            self.saveLdapContact(tmp_id, vals, cursor, uid, context)
        return tmp_id

    def write_ldap(self, cursor, uid, ids, vals, context=None):
        context = context or {}
        self.getconn(cursor, uid, {})
        if not isinstance(ids, list):
            ids = [ids]
        if ids:
            self.validate_entries(vals, cursor, uid, ids)
        if context.has_key('init_mode') and context['init_mode']:
            success = True
        else:
            success = super(LDAPAddress, self).write_ldap(cursor, uid, ids,
                                                     vals, context)
        if self.ldaplinkactive(cursor, uid, context):
            for address_id in ids:
                self.updateLdapContact(address_id, vals, cursor, uid, context)
        return success

    def unlink(self, cursor, uid, ids, context=None):
        if not context: context = {}
        if ids:
            self.getconn(cursor, uid, {})
            if not isinstance(ids, list):
                ids = [ids]
            if self.ldaplinkactive(cursor, uid, context):
                for id in ids:
                    self.removeLdapContact(id, cursor, uid)
        return super(LDAPAddress, self).unlink(cursor, uid, ids)

    def validate_entries(self, vals, cursor, uid, ids):
        """Validate data of an address based on the inetOrgPerson schema"""
        for val in vals:
            try:
                if isinstance(vals[val], basestring):
                    vals[val] = unicode(vals[val].decode('utf8'))
            except UnicodeError:
                logger.notifyChannel('LDAP encode', netsvc.LOG_DEBUG,
                                     'cannot unicode ' + vals[val])
                pass

        if ids is not None:
            if isinstance(ids, (int, long)):
                ids = [ids]
            if len(ids) == 1:
                self.addNeededFields(ids[0], vals, cursor, uid)
        email = vals.get('email', False)
        phone = vals.get('phone', False)
        fax = vals.get('fax', False)
        mobile = vals.get('mobile', False)
        name = vals.get('name', False)

        if email:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
                        email) is None:
                raise osv.except_osv(_('Warning !'),
                                     _('Please enter a valid e-mail'))
        phones = (('phone', phone), ('fax', fax), ('mobile', mobile))
        for phone_tuple in phones:
            phone_number = phone_tuple[1]
            #if phone_number:
            #    if not phone_number.startswith('+'):
            #        raise osv.except_osv(_('Warning !'),
            #                             _('Please enter a valid phone number in %s'
            #                               ' international format (i.e. leading +)') % phone_tuple[0])

    def getVals(self, att_name, key, vals, dico, uid, ids, cursor, context=None):
        """map to values to dict"""
        if not context: context = {}
        ## We explicitely test False value
        if vals.get(key, False) != False:
            dico[att_name] = vals[key]
        else:
            if context.get('init_mode'):
                return False
            tmp = self.read(cursor, uid, ids, [key], context={})
            if tmp.get(key, False):
                dico[att_name] = tmp[key]

    def _un_unicodize_buf(self, in_buf):
        if isinstance(in_buf, unicode):
            try:
                return in_buf.encode()
            except Exception, e:
                return unicodedata.normalize("NFKD", in_buf).encode('ascii', 'ignore')
        return in_buf

    def unUnicodize(self, indict):
        """remove unicode data of modlist as unicode is not supported
            by python-ldap librairy till version 2.7"""
        for key in indict:
            if not isinstance(indict[key], list):
                indict[key] = self._un_unicodize_buf(indict[key])
            else:
                nonutfArray = []
                for val in indict[key]:
                    nonutfArray.append(self._un_unicodize_buf(val))
                indict[key] = nonutfArray

    def addNeededFields(self, id, vals, cursor, uid):
        keys = vals.keys()
        previousvalue = self.browse(cursor, uid, [id])[0]
        if not vals.get('id'):
            vals['id'] = previousvalue.id
        values_to_check = ('email', 'phone', 'fax', 'mobile', 'name',
                           'street', 'street2')
        for val in values_to_check:
            if not vals.get(val):
                vals[val] = previousvalue[val]


    def mappLdapObject(self, id, vals, cursor, uid, context):
        """Mapp ResPArtner adress to moddlist"""
        self.addNeededFields(id, vals, cursor, uid)
        conn = self.getconn(cursor, uid, {})
        keys = vals.keys()
        partner_obj = self.pool.get('res.partner')
        name = partner_obj.browse(cursor, uid, vals['id']).name
        vals['partner'] = name
        if name:
            cn = name

        contact_obj = {'objectclass': ['inetOrgPerson'],
                       'uid': [str(id)],
                       'ou': [conn.OU],
                       'cn': [name],
                       'sn': [name]
                       }
        if not vals.get('street'):
            vals['street'] = u''
        if not vals.get('street2'):
            vals['street2'] = u''
        street_key = 'street'
        if self.getconn(cursor, uid, {}).ACTIVDIR:
            # ENTERING THE M$ Realm and it is weird
            # We manage the address
            street_key = 'streetAddress'
        contact_obj[street_key] = vals['street'] + "\r\n" + vals['street2']
        # we modifiy the class


        # we handle the state
        if vals.get('state_id'):
            state = self.browse(cursor, uid, id).state_id.name
            if state:
                vals['state_id'] = state

        else:
            vals['state_id'] = False

        if vals.get('state_id', False):
            self.getVals('st', 'state_id', vals, contact_obj, uid, id, cursor, context)

        # we compute the display name
        vals['displayName'] = '%s %s' % (vals['partner'], contact_obj['cn'][0])
        # we get the title
        if self.browse(cursor, uid, id).function:
            contact_obj['description'] = self.browse(cursor, uid, id).function
        # we replace carriage return
        if vals.get('comment', False):
            vals['comment'] = vals['comment'].replace("\n", "\r\n")

        self.getVals('description', 'comment', vals, contact_obj, uid, id, cursor, context)
        self.getVals('displayName', 'partner', vals, contact_obj, uid, id, cursor, context)
        self.getVals('departmentNumber', 'function', vals, contact_obj, uid, id, cursor, context)
        self.getVals('labeledURI', 'website', vals, contact_obj, uid, id, cursor, context)


        # Common attributes
        # self.getVals('givenName', 'firstname', vals, contact_obj, uid, id, cursor, context)
        self.getVals('mail', 'email', vals, contact_obj, uid, id, cursor, context)
        self.getVals('telephoneNumber', 'phone', vals, contact_obj, uid, id, cursor, context)
        self.getVals('l', 'city', vals, contact_obj, uid, id, cursor, context)
        self.getVals('facsimileTelephoneNumber', 'fax', vals, contact_obj, uid, id, cursor, context)
        self.getVals('mobile', 'mobile', vals, contact_obj, uid, id, cursor, context)

        self.getVals('postalCode', 'zip', vals, contact_obj, uid, id, cursor, context)
        self.unUnicodize(contact_obj)
        return contact_obj

    def saveLdapContact(self, id, vals, cursor, uid, context=None):
        """save openerp adress to ldap"""
        contact_obj = self.mappLdapObject(id, vals, cursor, uid, context)
        conn = self.connectToLdap(cursor, uid, context=context)
        try:
            if self.getconn(cursor, uid, context).ACTIVDIR:
                conn.connexion.add_s("CN=%s,OU=%s,%s" % (contact_obj['cn'][0], conn.OU, conn.CONTACT_DN),
                                     ldap.modlist.addModlist(contact_obj))
            else:
                conn.connexion.add_s("CN=%s,OU=%s,%s" % (contact_obj['cn'][0], conn.OU, conn.CONTACT_DN),
                                     ldap.modlist.addModlist(contact_obj))
        except Exception, e:
            raise e
        conn.connexion.unbind_s()

    def updateLdapContact(self, id, vals, cursor, uid, context):
        """update an existing contact with the data of OpenERP"""
        conn = self.connectToLdap(cursor, uid, context={})
        try:
            old_contatc_obj = self.getLdapContact(conn, id)
        except ldap.NO_SUCH_OBJECT:
            self.saveLdapContact(id, vals, cursor, uid, context)
            return
        contact_obj = self.mappLdapObject(id, vals, cursor, uid, context)
        if conn.ACTIVDIR:
            modlist = []
            for key, val in contact_obj.items():
                if key in ('cn', 'uid', 'objectclass'):
                    continue
                if isinstance(val, list):
                    val = val[0]
                modlist.append((ldap.MOD_REPLACE, key, val))
        else:
            modlist = ldap.modlist.modifyModlist(old_contatc_obj[1], contact_obj)
        try:
            conn.connexion.modify_s(old_contatc_obj[0], modlist)
            conn.connexion.unbind_s()
        except Exception, e:
            raise e

    def removeLdapContact(self, id, cursor, uid):
        """Remove a contact from ldap"""
        conn = self.connectToLdap(cursor, uid, context={})
        to_delete = None
        try:
            to_delete = self.getLdapContact(conn, id)
        except ldap.NO_SUCH_OBJECT:
            logger.notifyChannel("Warning", netsvc.LOG_INFO,
                                 _("'no object to delete in ldap' %s") % (id))
        except Exception, e:
            raise e
        try:
            if to_delete:
                conn.connexion.delete_s(to_delete[0])
                conn.connexion.unbind_s()
        except Exception, e:
            raise e

    def getLdapContact(self, conn, id):
        result = conn.connexion.search_ext_s("ou=%s,%s" % (conn.OU, conn.CONTACT_DN),
                                             ldap.SCOPE_SUBTREE,
                                             "(&(objectclass=*)(uid=" + str(id) + "))"
                                             )
        if not result:
            raise ldap.NO_SUCH_OBJECT
        return result[0]

    def ldaplinkactive(self, cursor, uid, context=None):
        """Check if ldap is activated for this company"""
        user = self.pool.get('res.users').browse(cursor, uid, uid, context=context)
        company = self.pool.get('res.company').browse(cursor, uid, user.company_id.id, context=context)
        return company.ldap_active

    def getconn(self, cursor, uid, context=None):
        """LdapConnMApper"""
        if not self.ldapMapper:
            self.ldapMapper = LdapConnMApper(cursor, uid, self)
        return self.ldapMapper

    def connectToLdap(self, cursor, uid, context=None):
        """Reinitialize ldap connection"""
        # getting ldap pref
        if not self.ldapMapper:
            self.getconn(cursor, uid, context)
        self.ldapMapper.get_connexion()
        return self.ldapMapper


LDAPAddress()
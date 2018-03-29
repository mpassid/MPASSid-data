
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Haltu Oy, http://haltu.fi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import hashlib
import logging
import string

import ldap

from authdata.datasources.base import ExternalDataSource

LOG = logging.getLogger(__name__)


class LDAPDataSource(ExternalDataSource):
  """
  Abstract base class for implementing external LDAP data sources.

  Implementations must provide values for:
    ldap_server: address of the server
    ldap_username: name for binding
    ldap_password: password for binding
    ldap_base_dn: base distinguished name for the queries

  KWARGS dictionary in configuration should be in the format:
    {
      'host': connection string for ldap server,
      'username': name to bind as,
      'password': password
    }
  """
  ldap_server = None
  ldap_username = None
  ldap_password = None
  ldap_base_dn = None

  connection = None

  municipality_id_map = {
    # 'municipality': '1234567-8',
  }

  school_id_map = {
    # 'school': '00001',
  }

  external_source = 'ldap'

  def __init__(self, host, username, password, *args, **kwargs):
    self.ldap_server = host
    self.ldap_username = username
    self.ldap_password = password
    if 'external_source' in kwargs:
      self.external_source = kwargs['external_source']
    LOG.debug('LDAPDataSource initialized',
        extra={'data': {'external_source': self.external_source}})
    super(LDAPDataSource, self).__init__(*args, **kwargs)

  def get_municipality_id(self, name):
    return self.municipality_id_map.get(name, name)

  def get_school_id(self, name):
    return self.school_id_map.get(name, name)

  def connect(self):
    """
    Initialize connection the the LDAP server.
    After this method is executed, self.connection is ready for executing
    queries.
    """
    # TODO: error handling
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    self.connection = ldap.initialize(self.ldap_server)
    self.connection.set_option(ldap.OPT_REFERRALS, 0)
    self.connection.simple_bind_s(self.ldap_username, self.ldap_password)

  def query(self, query_filter):
    """
    query ldap with the provided filter string
    """
    if not self.connection:
      self.connect()
    # TODO: LDAP error handling
    # TODO: must get exactly one result
    return self.connection.search_s(self.ldap_base_dn, filterstr=query_filter, scope=ldap.SCOPE_SUBTREE)


class TestLDAPDataSource(LDAPDataSource):
  """
  Example result from test_ldap

   ('cn=bar,ou=Opettajat,ou=People,ou=LdapKoulu1,ou=KuntaYksi,dc=mpass-test,dc=csc,dc=fi',
    {'cn': ['bar'],
     'givenName': ['Ldap'],
     'mail': ['bar@mpass-test.invalid'],
     'objectClass': ['top', 'inetOrgPerson'],
     'sn': ['Opettaja10013'],
     'title': ['Opettaja'],
     'uid': ['bar'],
     'userPassword': ['foo']})

   ('cn=bar,ou=Oppilaat,ou=People,ou=LdapKoulu1,ou=KuntaYksi,dc=mpass-test,dc=csc,dc=fi',
    {'cn': ['bar'],
     'departmentNumber': ['6C'],
     'givenName': ['Ldap'],
     'mail': ['bar@mpass-test.invalid'],
     'objectClass': ['top', 'inetOrgPerson'],
     'sn': ['Oppilas352'],
     'title': ['Oppilas'],
     'uid': ['bar'],
     'userPassword': ['foo']}),

  """

  external_source = 'ldap_test'

  municipality_id_map = {
    'KuntaYksi': '1234567-8'
  }

  class _schoolid_generator():
    """
    generator for fake school ids
    """
    @classmethod
    def get(cls, name, default=None):
      num = ''.join(i for i in name if i in string.digits)
      return '%05d' % int(num)

  school_id_map = _schoolid_generator

  # 'LdapKoulu1': '00001',
  # 'LdapKoulu2': '00002',
  # 'LdapKoulu3': '00003',
  # 'LdapKoulu4': '00004',
  # 'LdapKoulu5': '00005',
  # 'LdapKoulu6': '00006',
  # 'LdapKoulu7': '00007',
  # 'LdapKoulu8': '00008',
  # 'LdapKoulu9': '00009',
  # 'LdapKoulu10': '00010',
  # 'LdapKoulu11': '00011',
  # etc...

  def __init__(self, *args, **kwargs):
    self.ldap_base_dn = 'ou=KuntaYksi,dc=mpass-test,dc=csc,dc=fi'
    self.ldap_filter = "(&(cn={value})(objectclass=inetOrgPerson))"
    """
    ldap_filter = Filter for finding the required user in an LDAP query,
                  for example "(&(attribute={value})(objectclass=inetOrgPerson))"
                  Query will substitue {value} with Auth Proxy's attribute query value.
    """
    super(TestLDAPDataSource, self).__init__(*args, **kwargs)

  def get_oid(self, username):
    """
    There is no OID information in this external source. Generate fake OID
    from username.
    """
    # TODO: OID is cut to 30 chars due to django username limitation
    return 'MPASSOID.{user_hash}'.format(user_hash=hashlib.sha1('ldap_test' + username).hexdigest())[:30]

  def normalizeString(self, string):
    return string.decode('unicode_escape').encode('iso8859-1').decode('utf8')

  def get_data(self, external_id):
    try:
      import time
      startstamp = int(time.time() * 1000)
      query_result = self.query(self.ldap_filter.format(value=external_id))[0]
      LOG.debug("LDAP query took " + str(int(time.time() * 1000) - startstamp) + " ms")
    except IndexError:
      return None
    dn_parts = query_result[0].split(',')
    first_name = self.normalizeString(query_result[1]['givenName'][0])
    last_name = self.normalizeString(query_result[1]['sn'][0])
    oid = self.get_oid(external_id)
#    attributes = []
    m = hashlib.md5()
    m.update(external_id)
    attributes = [{'name':'legacyId', 'value':m.hexdigest()}, {'name':'municipalityCode', 'value':'1'}]
    roles = [{
      'school': self.normalizeString(dn_parts[3].replace("ou=","")),
#      'school': self.normalizeString(dn_parts[3].strip("ou=")),
      'role': self.normalizeString(query_result[1]['title'][0]),
      'municipality': self.normalizeString(dn_parts[4].replace("ou=","")),
#      'municipality': self.normalizeString(dn_parts[4].strip("ou=")),
      'group': query_result[1].get('departmentNumber', [''])[0]
    }]

    # Provision
    self.provision_user(oid, external_id)

    return {
      'username': oid,
      'first_name': first_name,
      'last_name': last_name,
      'roles': roles,
      'attributes': attributes
    }

  def get_user_data(self, request):
    ldap_filter = "objectclass=inetOrgPerson"
    query_base = self.ldap_base_dn
    if 'school' in request.GET:
      self.ldap_base_dn = 'ou=%s,%s' % (request.GET['school'], query_base)
    if 'group' in request.GET and request.GET['group'] != '':
      ldap_filter = '(&(departmentNumber=%s)(%s))' % (request.GET['group'], ldap_filter)
    query_results = self.query(ldap_filter)
    response = []

    for result in query_results:
      dn_parts = result[0].split(',')
      username = result[1]['cn'][0]
      first_name = result[1]['givenName'][0]
      last_name = result[1]['sn'][0]
      external_id = result[1]['uid'][0]
#      oid = self.get_oid(username)
      oid = self.get_oid(external_id)
      attributes = [
        # TODO: what attributes should be returned from LDAP?
      ]
      roles = [{
        'school': self.get_school_id(dn_parts[3].strip("ou=")),
        'role': result[1]['title'][0],
        'municipality': self.get_municipality_id(dn_parts[4].strip("ou=")),
        'group': result[1].get('departmentNumber', [''])[0]
      }]
      response.append({
        'username': oid,
        'first_name': first_name,
        'last_name': last_name,
        'roles': roles,
        'attributes': attributes
      })

      # Provision
      self.provision_user(oid, external_id)

    # TODO: support actual paging via SimplePagedResultsControl
    return {
      'count': len(response),
      'next': None,
      'previous': None,
      'results': response,
    }

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2


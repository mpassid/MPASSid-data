
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
#

"""
External data source implementations
"""

import base64
import hashlib
import logging

import ldap

from authdata.datasources.ldap_base import LDAPDataSource

LOG = logging.getLogger(__name__)


class OuluLDAPDataSource(LDAPDataSource):
  """
  Required configuration parameters:
    host
    username
    password
    base_dn
  """

  external_source = 'ad_oulu'

  municipality_id_map = {
    'Oulu': '0187690-1'
  }

  school_id_map = {
    u'Herukan koulu': '06347',
    u'Hintan koulu': '06329',
    u'Hönttämäen koulu': '03367',
    u'Kaakkurin koulu': '03748',
    u'Karjasillan yläaste': '06315',
    u'Kastellin koulu': '06316',
    u'Kaukovainion koulu': '06330',
    u'Knuutilankankaan koulu': '03515',
    u'Korvensuoran koulu': '06334',
    u'Koskelan koulu': '06335',
    u'Kuivasjärven ala-aste': '06336',
    u'Laanilan yläaste': '06318',
    u'Lintulammen koulu': '06339',
    u'Madekosken ala-aste': '06337',
    u'Maikkulan koulu': '03600',
    u'Merikosken yläaste': '06320',
    u'Metsokankaan koulu': '03780',
    u'Myllyojan koulu': '03262',
    u'Myllytullin koulu': '06322',
    u'Nuottasaaren koulu': '06340',
    u'Oulujoen koulu': '06341',
    u'Oulun kansainvälinen koulu': '03735',
    u'Oulunlahden koulu': '06332',
    u'Pateniemen yläaste': '06323',
    u'Paulaharjun koulu': '06344',
    u'Pikkaralan ala-aste': '06345',
    u'Pohjankartanon yläaste': '06847',
    u'Pöllönkankaan koulu': '06319',
    u'Rajakylän koulu': '06346',
    u'Ritaharjun koulu': '03802',
    u'Terva-Toppilan koulu': '06324',
    u'Teuvo Pakkalan koulu': '06348',
    u'Tuiran ala-aste': '06350',
    u'Vesalan koulu': '06446',
    u'Ylikiimingin koulu': '06437',
    u'Heinätorin koulu': '06327',
    u'Kajaanintullin koulu': '08858',
    u'Karjasillan lukio': '00265',
    u'Kastellin lukio': '00603',
    u'Laanilan lukio': '00401',
    u'Madetojan musiikkilukio': '00604',
    u'Merikosken lukio': '00831',
    u'Oulun Suom. Yhteiskoulun lukio': '00601',
    u'Oulun aikuislukio': '00548',
    u'Oulun lyseon lukio': '00598',
    u'Pateniemen lukio': '00674',
    u'Oulun konservatorio': '01968',
    u'Oulu-opisto': '02246',
  }

  def __init__(self, base_dn, *args, **kwargs):
    self.ldap_base_dn = base_dn
    # self.ldap_filter = "(|(sAMAccountName={value})(userPrincipalName={value}@eduouka.fi))"
    self.ldap_filter = "(objectGUID={value})"
    """
    ldap_filter = Filter for finding the required user in an LDAP query,
                  for example "(&(attribute={value})(objectclass=inetOrgPerson))"
                  Query will substitue {value} with Auth Proxy's attribute query value.
    """
    super(OuluLDAPDataSource, self).__init__(*args, **kwargs)

  def connect(self):
    """
    Initialize a secure connection the the LDAP server.
    """
    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, 'oulu_certificate')
    self.connection = ldap.initialize(self.ldap_server)
    self.connection.set_option(ldap.OPT_REFERRALS, 0)
    self.connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    self.connection.set_option(ldap.OPT_X_TLS_DEMAND, True)
    self.connection.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
    self.connection.start_tls_s()
    self.connection.simple_bind_s(self.ldap_username, self.ldap_password)

  def get_oid(self, username):
    """
    There is no OID information in this external source. Generate fake OID
    from username.
    """
    # TODO: OID is cut to 30 chars due to django username limitation
    return 'MPASSOID.{user_hash}'.format(user_hash=hashlib.sha1('ad_oulu' + username).hexdigest())[:30]

  def get_external_id(self, query_result):
    # TODO: Check if this works
    if 'uid' not in query_result[1]:
      LOG.error('FIX IMPLEMENTATION. Get right user id',
          extra={'data': {'query_result': query_result}})

    return query_result[1]['uid'][0]

  def get_username(self, query_result):
    return query_result[1]['objectGUID'][0]

  def get_first_name(self, query_result):
    return query_result[1].get('givenName', [u''])[0]

  def get_last_name(self, query_result):
    return query_result[1].get('sn', [u''])[0]

  def get_municipality(self):
    return u'Oulu'

  def get_school(self, query_result):
    return query_result[1].get('physicalDeliveryOfficeName', [u''])[0]

  def get_role(self, query_result):
    return query_result[1].get('title', [u''])[0]

  def get_group(self, query_result):
    return query_result[1].get('department', [u''])[0]

  def get_data(self, external_id):
    try:
      # search term is an objectGUID. it needs to be decoded to a byte string
      # for querying ldap
      object_guid = base64.b64decode(external_id)
      query_result = self.query(self.ldap_filter.format(value=object_guid))[0]
    except IndexError:
      return None
    username = self.get_username(query_result)
    first_name = self.get_first_name(query_result)
    last_name = self.get_last_name(query_result)
    oid = self.get_oid(username)
    attributes = []
    roles = [{
      'school': self.get_school_id(self.get_school(query_result)),
      'role': self.get_role(query_result),
      'municipality': self.get_municipality_id(self.get_municipality()),
      'group': self.get_group(query_result),
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
    ldap_filter = u'(&(objectCategory=person)(objectClass=user))'
    if 'school' in request.GET:
      ldap_filter = u'(&(physicalDeliveryOfficeName={school}){filter_base})'.format(school=request.GET['school'], filter_base=ldap_filter)
    if 'group' in request.GET and request.GET['group'] != '':
      ldap_filter = u'(&(department={group}){filter_base})'.format(group=request.GET['group'], filter_base=ldap_filter)
    query_results = self.query(ldap_filter)
    response = []

    for query_result in query_results:
      username = self.get_username(query_result)
      first_name = self.get_first_name(query_result)
      last_name = self.get_last_name(query_result)
      external_id = self.get_external_id(query_result)
      oid = self.get_oid(username)
      attributes = [
        # TODO: what attributes should be returned from LDAP?
      ]
      roles = [{
        'school': self.get_school_id(self.get_school(query_result)),
        'role': self.get_role(query_result),
        'municipality': self.get_municipality_id(self.get_municipality()),
        'group': self.get_group(query_result),
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


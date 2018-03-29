
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

import logging
from authdata.models import User, Source, Attribute, UserAttribute

LOG = logging.getLogger(__name__)


class ExternalDataSource(object):
  """
  An external user attribute source. The source is identified by a specific
  attribute name, which is configured in the project settings.

  This is a base class for all external data sources
  """

  external_source = ''

  def __init__(self, *args, **kwargs):
    pass

  def get_oid(self, username):
    """
    Generate MPASS OID for user from the username

    Not needed if authentication source returns proper oid
    """
    raise NotImplementedError

  def get_data(self, external_id):
    """
    Get user data based on attribute query.

    external_id: attribute value passed by Auth Proxy
    """
    raise NotImplementedError

  def get_user_data(self, request):
    """
    Query for a user listing.

    request: the request object containing GET-parameters for filtering the query
    """
    raise NotImplementedError

  def provision_user(self, oid, external_id):
    """
    Save fetched user to local db

    oid: MPASS identifier
    external_id: id of the user in the external data source
    """

    user_obj, new_user_created = User.objects.get_or_create(username=oid)
    LOG.debug('User provision',
            extra={'data':
                   {'oid': oid, 'external_id': external_id,
                    'external_source': self.external_source,
                    'new_user_created': new_user_created,
                    }})
    user_obj.external_id = external_id
    user_obj.external_source = self.external_source
    user_obj.save()

    source_obj, _ = Source.objects.get_or_create(name='local')
    attribute_obj, _ = Attribute.objects.get_or_create(name=self.external_source)

    user_attr_obj, _ = UserAttribute.objects.get_or_create(user=user_obj,
        attribute=attribute_obj, data_source=source_obj)
    user_attr_obj.value = external_id
    user_attr_obj.save()
    LOG.debug('User attribute added',
        extra={'data':
              {'oid': oid, 'external_id': external_id,
               'external_source': self.external_source,
               'new_user_created': new_user_created,
               'source_name': 'local'}})


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2


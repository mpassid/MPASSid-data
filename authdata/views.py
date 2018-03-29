
# -*- encoding: utf-8 -*-

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
import datetime
import importlib
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import filters
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
import django_filters
from authdata.serializers import QuerySerializer, UserSerializer, AttributeSerializer, UserAttributeSerializer, MunicipalitySerializer, SchoolSerializer, RoleSerializer, AttendanceSerializer
from authdata.models import User, Attribute, UserAttribute, Municipality, School, Role, Attendance

LOG = logging.getLogger(__name__)


def get_external_user_data(external_source, external_id):
  """
  Raises ImportError if external source configuration is wrong
  """
  source = settings.AUTH_EXTERNAL_SOURCES[external_source]
  LOG.debug('Trying to import module of external authentication source', extra={'data': {'module_name': source[0]}})
  handler_module = importlib.import_module(source[0])
  kwargs = source[2]
  handler = getattr(handler_module, source[1])(**kwargs)
  return handler.get_data(external_id)


class QueryView(generics.RetrieveAPIView):
  """ Returns information about one user.

  The ``username`` is global unique identifier for the user.

  The ``roles`` is a list of roles the user has in different schools.
  User can have multiple roles in one school.

  Possible values for ``role`` are ``teacher`` and ``student``.

  Query is made by GET parameters. Only one parameter is allowed. The parameter
  consists of an attribute name and an attribute value.

  ``Not found`` is returned if:

  * the parameter name is not recognized
  * multiple results would be returned (only one result is allowed)
  * no parameters are specified
  """
  queryset = User.objects.all()
  serializer_class = QuerySerializer
  lookup_field = 'username'

  def get(self, request, *args, **kwargs):
    # 1. look for a user object matching the query parameter. if it's found, check if it's an external user and fetch data
    try:
      user_obj = self.get_object()
    except Http404:
      user_obj = None
    if user_obj:
      # local user object exists.
      if user_obj.external_source and user_obj.external_id:
        # user is an external user. fetch data from source.
        try:
          user_data = get_external_user_data(user_obj.external_source, user_obj.external_id)
        except ImportError:
          LOG.error('Can not import external authentication source', extra={'data': {'external_source': repr(user_obj.external_source)}})
          return Response(None)
        except KeyError:
          LOG.error('External source not configured', extra={'data': {'external_source': repr(user_obj.external_source)}})
          return Response(None)
        if user_data is None:
          # queried user does not exist in the external source
          return Response(None)
        for user_attribute in user_obj.attributes.all():
          # Add attributes to user data
          user_data['attributes'].append({'name': user_attribute.attribute.name, 'value': user_attribute.value})
        LOG.debug('/query returning data', extra={'data': {'user_data': repr(user_data)}})
        return Response(user_data)
    else:
      # 2. if user was not found and query parameter is mapped to an external source, fetch and create user
      for attr in request.GET.keys():
        if attr in settings.AUTH_EXTERNAL_ATTRIBUTE_BINDING:
          try:
            user_data = get_external_user_data(settings.AUTH_EXTERNAL_ATTRIBUTE_BINDING[attr], request.GET.get(attr))
            if user_data is None:
              # queried user does not exist in the external source
              return Response(None)

            # New users are created in data source
            user_obj = User.objects.get(username=user_data['username'])
            for user_attribute in user_obj.attributes.all():
              # Add attributes to user data
              user_data['attributes'].append({'name': user_attribute.attribute.name, 'value': user_attribute.value})
            LOG.debug('/query returning data', extra={'data': {'user_data': repr(user_data)}})
            return Response(user_data)

          except ImportError as e:
            LOG.error('Could not import external data source',
                extra={'data': {'error': unicode(e), 'attr': repr(attr)}})
            # TODO: error handling
            # flow back to normal implementation most likely return empty
        break
    return super(QueryView, self).get(request, *args, **kwargs)

  def get_object(self):
    qs = self.filter_queryset(self.get_queryset())
    qs = qs.distinct()
    filter_kwargs = {}
    lookup = self.kwargs.get(self.lookup_field, None)
    if lookup:
      filter_kwargs = {self.lookup_field: lookup}
    else:
      for k, v in self.request.GET.iteritems():
        a = get_object_or_404(Attribute.objects.all(), name=k)
        filter_kwargs['attributes__attribute__name'] = a.name
        filter_kwargs['attributes__value'] = v
        filter_kwargs['attributes__disabled_at__isnull'] = True
        break  # only handle one GET variable for now
      else:
        raise Http404
    obj = generics.get_object_or_404(qs, **filter_kwargs)
    self.check_object_permissions(self.request, obj)
    return obj


class UserFilter(django_filters.FilterSet):
  municipality = django_filters.CharFilter(name='attendances__school__municipality__name', lookup_expr='iexact')
  school = django_filters.CharFilter(name='attendances__school__name', lookup_expr='iexact')
  group = django_filters.CharFilter(name='attendances__group', lookup_expr='iexact')
  # changed_at = django_filters.MethodFilter(action='timestamp_filter')
  # RR 2018-02-28
  changed_at = django_filters.BooleanFilter(name='attendance__timestamp__validity', method='timestamp_filter')


  def timestamp_filter(self, queryset, value):
    # TODO: this is unaware of removed UserAttributes
    try:
      tstamp = datetime.datetime.fromtimestamp(float(value))
    except ValueError:
      return queryset.none()
    by_user = Q(modified__gte=tstamp)
    by_user_attribute = Q(attributes__modified__gte=tstamp)
    by_attribute_name = Q(attributes__attribute__modified__gte=tstamp)
    by_attendance = Q(attendances__modified__gte=tstamp)
    by_role_name = Q(attendances__role__modified__gte=tstamp)
    # SELECT DISTINCT ON ("authdata_user"."id") - makes this query perform a lot faster,
    # but is ONLY compatible with PostgreSQL!
    return queryset.filter(by_user | by_user_attribute | by_attribute_name | by_attendance | by_role_name).distinct('id')

  class Meta:
    model = User
    fields = ['username', 'school', 'group', 'changed_at']


class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all().distinct()
  serializer_class = UserSerializer
  # filter_backends = (filters.DjangoFilterBackend,)
  # Removed DjangoFilterBackend inline with deprecation policy. Use django_filters.rest_framework.FilterSet and/or 
  # django_filters.rest_framework.DjangoFilterBackend instead. #5273
  # RR 2018-02-28
  filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
  filter_class = UserFilter

  def list(self, request, *args, **kwargs):
    if 'municipality' in request.GET and request.GET['municipality'].lower() in [binding_name.lower() for binding_name in settings.AUTH_EXTERNAL_MUNICIPALITY_BINDING.keys()]:
      for binding_name, binding in settings.AUTH_EXTERNAL_MUNICIPALITY_BINDING.iteritems():
        if binding_name.lower() == request.GET['municipality'].lower():
          source = settings.AUTH_EXTERNAL_SOURCES[binding]
      try:
        handler_module = importlib.import_module(source[0])
        k = source[2]
        handler = getattr(handler_module, source[1])(**k)
        user_data = handler.get_user_data(request)
        LOG.debug('/user returning data', extra={'data': {'user_data': repr(user_data)}})
        return Response(user_data)
      except ImportError as e:
        LOG.error('Could not import external data source',
                extra={'data': {'error': unicode(e)}})
        # TODO: error handling
        # flow back to normal implementation most likely return empty

    return super(UserViewSet, self).list(request, *args, **kwargs)


class AttributeViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Attribute.objects.all()
  serializer_class = AttributeSerializer


class UserAttributeFilter(django_filters.FilterSet):
  user = django_filters.CharFilter(name='user__username', lookup_expr='exact')
  attribute = django_filters.CharFilter(name='attribute__name', lookup_expr='exact')

  class Meta:
    model = UserAttribute
    fields = ['user', 'attribute']


class UserAttributeViewSet(viewsets.ModelViewSet):
  queryset = UserAttribute.objects.filter(disabled_at__isnull=True)
  serializer_class = UserAttributeSerializer
  # filter_backends = (filters.DjangoFilterBackend,)
  # Removed DjangoFilterBackend inline with deprecation policy. Use django_filters.rest_framework.FilterSet and/or 
  # django_filters.rest_framework.DjangoFilterBackend instead. #5273
  # RR 2018-02-28
  filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

  filter_class = UserAttributeFilter

  def destroy(self, request, *args, **kwargs):
    # UserAttribute is flagged as disabled
    obj = self.get_object()
    obj.disabled_at = datetime.datetime.now()
    obj.save()
    return Response(status=204)


class MunicipalityViewSet(viewsets.ModelViewSet):
  queryset = Municipality.objects.all()
  serializer_class = MunicipalitySerializer


class SchoolViewSet(viewsets.ModelViewSet):
  queryset = School.objects.all()
  serializer_class = SchoolSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Role.objects.all()
  serializer_class = RoleSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
  queryset = Attendance.objects.all()
  serializer_class = AttendanceSerializer

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2



# -*- coding: utf-8 -*-
# pylint: disable=locally-disabled, no-member

from mock import Mock
from django.test import TestCase
from authdata import serializers
from authdata.tests import factories as f


class TestQuerySerializer(TestCase):

  def test_role_data(self):
    obj = serializers.QuerySerializer()
    self.assertTrue(obj)

    user_obj = f.UserFactory()
    attendance_obj = f.AttendanceFactory(user=user_obj)

    data = obj.role_data(user_obj)
    self.assertEqual(len(data), 1)

    d = {}
    d['school'] = attendance_obj.school.school_id
    d['group'] = attendance_obj.group
    d['role'] = attendance_obj.role.name
    d['municipality'] = attendance_obj.school.municipality.municipality_id

    self.assertEqual(data[0], d)

  def test_attribute_data(self):
    obj = serializers.QuerySerializer()
    self.assertTrue(obj)

    user_obj = f.UserFactory()
    user_attribute_obj = f.UserAttributeFactory(user=user_obj)

    data = obj.attribute_data(user_obj)
    self.assertEqual(len(data), 1)

    d = {}
    d['name'] = user_attribute_obj.attribute.name
    d['value'] = user_attribute_obj.value

    self.assertEqual(data[0], d)


class TestUserSerializer(TestCase):

  def test_attribute_data_no_request(self):
    obj = serializers.UserSerializer()
    self.assertTrue(obj)

    user_obj = f.UserFactory()
    user_attribute_obj = f.UserAttributeFactory(user=user_obj)

    data = obj.attribute_data(user_obj)
    self.assertEqual(len(data), 1)

    d = {}
    d['name'] = user_attribute_obj.attribute.name
    d['value'] = user_attribute_obj.value

    self.assertEqual(data[0], d)

  def test_attribute_data_with_request(self):
    obj = serializers.UserSerializer()
    self.assertTrue(obj)

    obj.context['request'] = Mock()
    obj.context['request'].user = Mock()
    obj.context['request'].user.username = u'foo'

    user_obj = f.UserFactory()
    user_attribute_obj = f.UserAttributeFactory(user=user_obj, data_source__name=u'foo')

    data = obj.attribute_data(user_obj)
    self.assertEqual(len(data), 1)

    d = {}
    d['name'] = user_attribute_obj.attribute.name
    d['value'] = user_attribute_obj.value

    self.assertEqual(data[0], d)


class TestUserAttributeSerializer(TestCase):

  def test_save(self):
    user_obj = f.UserFactory(username='foo')
    attribute_obj = f.AttributeFactory()

    data = {'attribute': attribute_obj.name,
            'user': user_obj.username}

    obj = serializers.UserAttributeSerializer(data=data)
    self.assertTrue(obj.is_valid(), 'Not Valid')

    obj.context['request'] = Mock()
    obj.context['request'].user = Mock()
    obj.context['request'].user.username = user_obj.username

    user_attribute_obj = obj.save()
    self.assertEqual(user_attribute_obj.attribute, attribute_obj)
    self.assertEqual(user_attribute_obj.user, user_obj)
    self.assertEqual(user_attribute_obj.data_source.name, user_obj.username)


class TestMuncipalitySerializer(TestCase):

  def test_save(self):
    user_obj = f.UserFactory(username='foo')

    data = {'name': 'municipality',
            'municipality_id': 'foo'}

    obj = serializers.MunicipalitySerializer(data=data)
    self.assertTrue(obj.is_valid(), 'Not Valid')

    obj.context['request'] = Mock()
    obj.context['request'].user = Mock()
    obj.context['request'].user.username = user_obj.username

    municipality = obj.save()
    self.assertEqual(municipality.data_source.name, user_obj.username)


class TestSchoolSerializer(TestCase):

  def test_save(self):
    user_obj = f.UserFactory(username='foo')
    muni_obj = f.MunicipalityFactory()

    data = {'name': 'school',
            'school_id': 'foo',
            'municipality': muni_obj.pk}

    obj = serializers.SchoolSerializer(data=data)
    self.assertTrue(obj.is_valid(), 'Not Valid')

    obj.context['request'] = Mock()
    obj.context['request'].user = Mock()
    obj.context['request'].user.username = user_obj.username

    school = obj.save()
    self.assertEqual(school.data_source.name, user_obj.username)


class TestAttendanceSerializer(TestCase):

  def test_save(self):
    user_obj = f.UserFactory(username='foo')
    school_obj = f.SchoolFactory()
    role_obj = f.RoleFactory()

    data = {'user': user_obj.pk,
            'school': school_obj.pk,
            'role': role_obj.pk,
            'group': 'Group1',
            }

    obj = serializers.AttendanceSerializer(data=data)
    self.assertTrue(obj.is_valid(), 'Not Valid')

    obj.context['request'] = Mock()
    obj.context['request'].user = Mock()
    obj.context['request'].user.username = user_obj.username

    attendance_obj = obj.save()
    self.assertEqual(attendance_obj.data_source.name, user_obj.username)


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2


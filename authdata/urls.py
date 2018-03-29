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
#

# RR 06.12.2017
# from django.conf.urls import patterns, include, url
from django.conf.urls import *

from django.contrib import admin
from rest_framework import routers
from authdata.views import QueryView
from authdata.views import UserViewSet, AttributeViewSet, UserAttributeViewSet, MunicipalityViewSet, SchoolViewSet, RoleViewSet, AttendanceViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'attribute', AttributeViewSet)
router.register(r'userattribute', UserAttributeViewSet)
router.register(r'municipality', MunicipalityViewSet)
router.register(r'school', SchoolViewSet)
router.register(r'role', RoleViewSet)
router.register(r'attendance', AttendanceViewSet)


# urlpatterns = patterns('',
# RR 2018-02-28
urlpatterns = [
    url(r'^api/1/user$', QueryView.as_view()),  # This should be removed as "/user" and "/user/" are now different which is confusing. User "/query/" instead
    url(r'^api/1/query(/(?P<username>[\w._-]+))?/?$', QueryView.as_view()),
    url(r'^api/1/', include(router.urls)),
    url(r'^sysadmin/', include(admin.site.urls)),
]

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2


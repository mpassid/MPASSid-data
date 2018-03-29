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

from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from authdata.forms import UserCreationForm, UserChangeForm
from authdata.models import Municipality
from authdata.models import School
from authdata.models import Role
from authdata.models import Attendance
from authdata.models import Source
from authdata.models import User
from authdata.models import Attribute
from authdata.models import UserAttribute


class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name',)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'role', 'group', 'data_source')
    list_filter = ('role', 'data_source')
    search_fields = ('school__school_id', 'school__name', 'school__municipality__name', 'user__username', 'group',)


class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class UserAttributeAdmin(admin.ModelAdmin):
    list_display = ('user', 'attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('user__username', 'value')


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name',)


class UserAttributeInline(admin.TabularInline):
    model = UserAttribute
    extra = 0


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('External source'), {'fields': ('external_source', 'external_id')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'external_source', 'external_id')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'external_source')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'external_id')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')
    inlines = [UserAttributeInline, AttendanceInline]
    form = UserChangeForm
    add_form = UserCreationForm


admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(UserAttribute, UserAttributeAdmin)


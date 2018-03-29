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

from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.forms import ReadOnlyPasswordHashField

from authdata.models import User


class UserCreationForm(forms.ModelForm):
  """
  A form that creates a user, with no privileges, from the given username and
  password.
  """
  error_messages = {
    'duplicate_username': _("A user with that username already exists."),
    'password_mismatch': _("The two password fields didn't match."),
  }
  username = forms.RegexField(label=_("Username"), max_length=30,
    regex=r'^[\w.@+-]+$',
    help_text=_("Required. 30 characters or fewer. Letters, digits and "
                "@/./+/-/_ only."),
    error_messages={
        'invalid': _("This value may contain only letters, numbers and "
                     "@/./+/-/_ characters.")})

  class Meta:
    model = User
    fields = ('username',)

  def clean_username(self):
    # Since User.username is unique, this check is redundant,
    # but it sets a nicer error message than the ORM. See #13147.
    username = self.cleaned_data["username"]
    try:
      User._default_manager.get(username=username)
    except User.DoesNotExist:
      return username
    raise forms.ValidationError(
      self.error_messages['duplicate_username'],
      code='duplicate_username',
    )

  def save(self, commit=True):
    user = super(UserCreationForm, self).save(commit=commit)
    user.set_unusable_password()
    user.save()
    return user


class UserChangeForm(forms.ModelForm):
  username = forms.RegexField(
      label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
      help_text=_("Required. 30 characters or fewer. Letters, digits and "
                  "@/./+/-/_ only."),
      error_messages={
          'invalid': _("This value may contain only letters, numbers and "
                       "@/./+/-/_ characters.")})
  password = ReadOnlyPasswordHashField(label=_("Password"),
      help_text=_("Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can change the password "
                  "using <a href=\"password/\">this form</a>."))

  class Meta:
    model = User
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(UserChangeForm, self).__init__(*args, **kwargs)
    f = self.fields.get('user_permissions', None)
    if f is not None:
      f.queryset = f.queryset.select_related('content_type')

  def clean_password(self):
    # Regardless of what the user provides, return the initial value.
    # This is done here, rather than on the field, because the
    # field does not have access to the initial value
    return self.initial['password']

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2


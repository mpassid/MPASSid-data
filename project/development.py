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

import sys
from project.settings import *

DEBUG = True
TEMPLATE_DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
      'level': 'DEBUG',
      'handlers': ['console'],
    },
    'formatters': {
      'normal': {
        'format': '%(asctime)s %(levelname)s %(name)s %(thread)d %(lineno)s %(message)s %(data)s'
      },
      'verbose': {
        'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s %(data)s'
      },
    },
    'filters': {
      'default': {
        '()': 'project.logging_helpers.Filter',
      },
    },
    'handlers': {
      'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
        'filters': ['default'],
      },
    },
    'loggers': {
      'django.db': {
        'level': 'WARNING',
        'handlers': ['console'],
        'propagate': True,
      },
      'django': {
        'level': 'INFO',
        'handlers': ['console'],
        'propagate': True,
      },
      '': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
      },
    },
}

if 'test' in sys.argv:
  INSTALLED_APPS += ('django_nose',)
  DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
  TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
  BROKER_BACKEND = 'memory'
  CELERY_ALWAYS_EAGER = True

  PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
  )

  EMAIL_BACKEND = 'django.core.mail.backend.locmem.EmailBackend'

  NOSE_ARGS = [
      '--verbosity=2',
      '--detailed-errors',
      '--nocapture',
  ]

# try:
#   from local_settings import *
# except ImportError:
#   pass

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2


# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django import VERSION as DJANGO_VERSION
import socket
import os
import warnings
from urlparse import urlparse

# Initializing xosconfig module
from xosconfig import Config
Config.init()

GEOIP_PATH = "/usr/share/GeoIP"
XOS_DIR = Config.get('xos_dir')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Enable CORS requests, needed to enable layered XOS
CORS_ORIGIN_ALLOW_ALL = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# LOGIN_REDIRECT_URL = '/admin/core/user'
LOGIN_REDIRECT_URL = '/admin/loggedin/'

MANAGERS = ADMINS

db_service = Config.get_service_info('xos-db')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': Config.get('database.name'),                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': Config.get('database.username'),
        'PASSWORD': Config.get('database.password'),
        'HOST': db_service['url'],                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': db_service['port'],                      # Set to empty string for default.
    }
}

AUTH_USER_MODEL = 'core.User'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Verbose warnings when a naive datetime is used, gives a traceback
# from: https://docs.djangoproject.com/en/1.9/topics/i18n/timezones/#code
warnings.filterwarnings(
        'error', r"DateTimeField .* received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/var/www/html/files/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/files/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = ( XOS_DIR + "/core/static/",
                     XOS_DIR + "/core/xoslib/static/",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'i0=a)c7_#2)5m%k_fu#%53xap$tlqc+#&z5as+bl7&)(@be_f9'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.GlobalRequestMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'xos.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'xos.wsgi.application'
# Default: 'csrftoken'
CSRF_COOKIE_NAME = 'xoscsrftoken'
# Default: 'django_language'
LANGUAGE_COOKIE_NAME = 'xos_django_language'
# Default: 'sessionid'
SESSION_COOKIE_NAME = 'xossessionid'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    XOS_DIR + "/templates",
#    XOS_DIR + "/core/xoslib/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django_extensions',
    'core',
    'services.syndicate_storage',
    # 'geoposition',
    # 'rest_framework_swagger',
)

# add services that were configured by xosbuilder to INSTALLED_APPS
if os.path.exists("/opt/xos/xos/xosbuilder_app_list"):
    for line in file("/opt/xos/xos/xosbuilder_app_list").readlines():
        line = line.strip()
        if line:
            INSTALLED_APPS = list(INSTALLED_APPS) + [line]

# Added for django-suit form
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    'core.context_processors.xos',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django_debug.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },'django.db.backends': {
            'level': 'WARNING',
        },
    }
}

XOS_BRANDING_NAME = "OpenCloud"
XOS_BRANDING_CSS = None
XOS_BRANDING_ICON = "/static/logo.png"
XOS_BRANDING_FAVICON = "/static/favicon.png"
XOS_BRANDING_BG = "/static/bg.png"

DISABLE_MINIDASHBOARD = False
ENCRYPTED_FIELDS_KEYDIR = XOS_DIR + '/private_keys'
ENCRYPTED_FIELD_MODE = 'ENCRYPT'

STATISTICS_DRIVER = "statistics_driver"

# prevents warnings on django 1.7
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# API key for Google Maps, created by zdw on 2016-06-29. Testing only, not for production
GEOPOSITION_GOOGLE_MAPS_API_KEY = 'AIzaSyBWAHP9mvLqWLRkVqK8o5wMskaIe9w7DaM'


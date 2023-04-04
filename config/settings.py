"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from django.utils.translation import ugettext_lazy as _
from decouple import config
import datetime as dt


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(BASE_DIR, 'secret_key.txt')) as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['sep.proforest.net', 'adminsep.proforest.net', 'www.sep.proforest.net', 'www.adminsep.proforest.net' ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #Complements:
    'cities_light',
    # 'django_filters',
    'django_js_reverse',
    'import_export',
    'widget_tweaks',
    #Import ApiRest:
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    #Import Cors headers
    'corsheaders',
    #import project apps
    'apps.dashboard.apps.DashboardConfig',
    'apps.company.apps.CompanyConfig',
    'apps.cities.apps.CitiesConfig',
    'apps.proforestform.apps.ProforestformConfig',
    'apps.formulario.apps.FormularioConfig',
    'apps.questionsbank.apps.QuestionsbankConfig',
    'apps.user.apps.UserConfig',
    'apps.traceability.apps.TraceabilityConfig',
    'apps.supplybase.apps.SupplybaseConfig',
    'apps.onedrive.apps.OnedriveConfig',
    'apps.emailcustom.apps.EmailcustomConfig',
    'apps.menu.apps.MenuConfig',


    #custom drf errors
    'drf_standardized_errors',

]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': dt.timedelta(minutes=480),
    'REFRESH_TOKEN_LIFETIME': dt.timedelta(days=1)
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #Corsheaders
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGES = (
    ('en', _('English')),
    ('es', _('Spanish')),
    ('pt', _('Portuguese')),

)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

if (DEBUG == True):
    STATICFILES_DIRS = [
        BASE_DIR / 'static/'
    ]
else:
    STATIC_ROOT = BASE_DIR / 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#=====    Custom Configurations    ===================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'
AUTH_USER_MODEL = 'user.User'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'
#=====================================================

#=====    Config send email PROVIDER = mailtrap  =====
EMAIL_HOST = 'live.smtp.mailtrap.io'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'api'
EMAIL_HOST_PASSWORD = 'dfe53296b0968b75045e6c9395f94056'
EMAIL_USE_TLS = True
EMAIL_FROM_DIR = 'notification@proforest.net'
DEFAULT_FROM_EMAIL = 'notification@proforest.net'
TEST = True
URL_PASSWORD_RESET = 'https://sep.proforest.net/#/home-public/?forgot='
URL_PASSWORD_RESET_DONE = 'https://sep.proforest.net/#/users/password/reset/done/'
#=====================================================

#HTTPS SETTINGS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
#===================================================

# HSTS SETTINGS
SECURE_HSTS_SECONDS = 15780000 # 1/2 year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#===================================================
#Configuration CORS TODO make only accepted
CORS_ALLOW_ALL_ORIGINS = True

CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en']
# CITIES_LIGHT_INCLUDE_COUNTRIES = ['CO']
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]
# GDAL_LIBRARY_PATH = '/opt/homebrew/opt/gdal/lib/libgdal.dylib'
# GEOS_LIBRARY_PATH = '/opt/homebrew/opt/geos/lib/libgeos_c.dylib'

#Default path for django_js_reverse
JS_REVERSE_OUTPUT_PATH = 'static/django_js_reverse/js/'

# Config CORS Module

CORS_ALLOW_METHODS = [
    'GET',
    'PUT',
    'POST',
    'PATCH',
    'DELETE',
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    'http://sep.proforest.net',
    'https://sep.proforest.net',
    'http://www.sep.proforest.net',
    'https://www.sep.proforest.net',
    'http://adminsep.proforest.net',
    'https://www.adminsep.proforest.net',
)

#Config One-Drive
URL_ONEDRIVE = 'https://graph.microsoft.com/v1.0/users/5c62e447-487f-4751-834e-2c4df9e5c91b/drive/root/children'
URL_GETFILE = 'https://graph.microsoft.com/v1.0/users/5c62e447-487f-4751-834e-2c4df9e5c91b/drive/items/'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_COOKIE_SECURE = True #to avoid transmitting the CSRF cookie over HTTP accidentally.
SESSION_COOKIE_SECURE = True #to avoid transmitting the session cookie over HTTP accidentally.

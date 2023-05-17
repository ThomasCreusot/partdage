"""
Django settings for Partdage project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import environ
import os
from pathlib import Path
import dj_database_url

# https://django-environ.readthedocs.io/en/latest/quickstart.html
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# https://django-environ.readthedocs.io/en/latest/quickstart.html
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The default value has been set again as the recommendation from django-environ quickstarts
# does not works with the codfe """ BASE_DIR.joinpath('templates'), """

# https://django-environ.readthedocs.io/en/latest/quickstart.html
# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# https://django-environ.readthedocs.io/en/latest/quickstart.html
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# https://django-environ.readthedocs.io/en/latest/quickstart.html
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'partdage.herokuapp.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',
    'sharingofexperience',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # https://whitenoise.readthedocs.io/en/stable/django.html
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Partdage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.joinpath('templates'),
        ],
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

WSGI_APPLICATION = 'Partdage.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

# https://django-environ.readthedocs.io/en/latest/quickstart.html
# Parse database connection url strings
# like psql://user:pass@127.0.0.1:8458/db
# DATABASES = {
#    # read os.environ['DATABASE_URL'] and raises
#    # ImproperlyConfigured exception if not found
#    #
#    # The db() method is an alias for db_url().
#    'default': env.db(),
#
#    # read os.environ['SQLITE_URL']
#    'extra': env.db_url(
#        'SQLITE_URL',
#        default='sqlite:////tmp/my-tmp-sqlite.db'
#    )
# }

# Change DATABASES for postgreSQL : LOCAL
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': env('DATABASE_NAME'),
#        'USER': env('DATABASE_USER'),
#        'PASSWORD': env('DATABASE_PASSWORD'),
#        'HOST': '127.0.0.1',
#        'PORT': '5432',
#    }
# }

# Change DATABASES for postgreSQL within docker compose
# https://github.com/docker/awesome-compose/tree/master/official-documentation-samples/django/
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': os.environ.get('POSTGRES_NAME'),
#        'USER': os.environ.get('POSTGRES_USER'),
#        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
#        'HOST': 'db',
#        'PORT': 5432,
#    }
# }


# Try fusion of both DATABASES previous setup
# PUT DATABASE_HOST=127.0.0.1 in .env file !
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'postgres'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DATABASE_HOST', 'db'),
        'PORT': 5432,
    }
}


# https://devcenter.heroku.com/articles/connecting-heroku-postgres#connecting-in-python
#DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
#sinon dans la commande de lancement !




"""
#https://pypi.org/project/dj-database-url/
DATABASES['default'] = dj_database_url.config(
    conn_max_age=600,
    conn_health_checks=True,
)
"""


"""
#TEST 18052023
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'postgres'),
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'db'),
    }
}
if os.environ.get('ON_HEROKU') == True:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
"""

"""
#TEST 18052023 -v 2
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'postgres'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DATABASE_HOST', 'db'),
        'PORT': 5432,
    }
}
#if os.environ.get('ON_HEROKU') == True:
#    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
#>does not work
"""

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# https://docs.djangoproject.com/en/4.1/howto/static-files/
# In addition to using a static/ directory inside your apps, you can define a list of directories
# (STATICFILES_DIRS) in your settings file where Django will also look for static files.
# You can namespace static assets in STATICFILES_DIRS by specifying prefixes.
# note: model: '/var/www/static/',
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# https://django-environ.readthedocs.io/en/latest/quickstart.html
# CACHES = {
#    # Read os.environ['CACHE_URL'] and raises
#    # ImproperlyConfigured exception if not found.
#    #
#    # The cache() method is an alias for cache_url().
#    'default': env.cache(),
#
#    # read os.environ['REDIS_URL']
#    'redis': env.cache_url('REDIS_URL')
# }

AUTH_USER_MODEL = 'authentication.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'


# https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# https://docs.djangoproject.com/en/4.0/howto/static-files/
# STATIC_ROOT = "/var/www/example.com/static/"
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# https://whitenoise.readthedocs.io/en/stable/django.html
STATIC_ROOT = BASE_DIR / "staticfiles"

# STORAGES = {
#    # ...
#    "staticfiles": {
#        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#    },
# }

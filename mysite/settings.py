"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os

from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "SECRET_KEY"

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = bool(os.environ.get("DEBUG", default=1))
DEBUG = bool(int(os.environ.get("DEBUG", 1)))

# SESSION_COOKIE_DOMAIN = "192.168.0.252"
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_SAMESITE = None  # Asegura compatibilidad
SESSION_COOKIE_SECURE = True  # Si usas HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.db"

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True


# HTTPS Config
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = False

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://192.168.0.252', 'https://localhost', 'https://192.168.0.130']

# Application definition

INSTALLED_APPS = [
    "daphne",
    'planilla.apps.PlanillaConfig',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # para servir archivos estáticos en desarrollo
    'django.contrib.sessions.middleware.SessionMiddleware',
    'planilla.middleware.ForceSessionDomainMiddleware',  # Agrega esto aquí
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],  # Configura el host de Redis
        },
    },
}


ASGI_APPLICATION = 'mysite.asgi.application'

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Cierra sesión al cerrar el navegador
SESSION_COOKIE_AGE = 86400  # 1 día de duración
SESSION_SAVE_EVERY_REQUEST = True  # Guarda sesión en cada request

ROOT_URLCONF = 'mysite.urls'

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR / "planilla" / "templates")],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", BASE_DIR / "postgres"),
        "USER": os.environ.get("SQL_USER", "postgres"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "db"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Buenos_Aires'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'planilla', 'static')  # 📌 Apunta a la carpeta local de desarrollo
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # 📌 Solo en producción

STATIC_URL = '/planilla/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "planilla", "staticfiles")  # Ruta donde se guardarán los estáticos en producción

MEDIA_ROOT = os.path.join(BASE_DIR, 'planilla/media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

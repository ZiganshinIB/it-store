from pathlib import Path
import os
from pathlib import Path
from .permissions import IsSuperUser
import dj_database_url
from django.conf.global_settings import AUTH_USER_MODEL
from environs import Env
env = Env()
env.read_env()


BASE_DIR = Path(__file__).resolve().parent.parent
#print(env.str('SECRET_KEY'))
SECRET_KEY = env.str('SECRET_KEY')

DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'person.apps.PersonConfig',
    'tasker.apps.TaskerConfig',

    'phonenumber_field',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',

    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


if env.str('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.parse(env.str('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
STATIC_URL = '/static/'
STATICFILES_DIRS = [
     os.path.join(BASE_DIR, "statics/"),
#     os.path.join(BASE_DIR, "bundles/"),
]
STATIC_ROOT = "/static"

AUTH_USER_MODEL = 'person.Person'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_RENDER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

}
DJOSER = {
    'SEND_ACTIVATION_EMAIL': False,
    'PASSWORD_RESET_CONFIRM_URL': False,
    'USERNAME_RESET_CONFIRM_URL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'SERIALIZERS': {
        'user_create': 'person.serializers.UserRegistrationSerializer',
        'user': 'person.serializers.PersonSerializer',

    },
    'PERMISSIONS':{
        'user_create': ['rest_framework.permissions.DjangoModelPermissions'],
        'user_delete': [IsSuperUser],
    }
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'IT Store API',
    'DESCRIPTION': 'Описание вашего API',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': '/api/v1/',  # Указываем префикс для схемы
    'SERVERS': [
        {'url': 'http://127.0.0.1:5080', 'description': 'Local server'},
        {'url': 'http://127.0.0.1:8000', 'description': 'Development server'},
    ],
    "SWAGGER_UI_FAVICON_HREF": STATIC_URL + "icon/api.png"
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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



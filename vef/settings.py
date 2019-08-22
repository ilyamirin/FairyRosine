import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'icllmxuu1j(tf1oybj9alm100im6whyg$_fz2e4xjqt=i-s4dg'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'channels',
    'coinCatalog',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'vef.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, '/coinCatalog/templates/coinCatalog/'),
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

WSGI_APPLICATION = 'vef.wsgi.application'
ASGI_APPLICATION = 'vef.routing.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


def configure_channel(ip='127.0.0.1', port=6379, backend='channels_redis.core.RedisChannelLayer', hosts=None):
    return {'CONFIG': {'hosts': hosts if hosts else [(ip, port)]}, 'BACKEND': backend}


local_ip = '10.60.17.34'
remote_ip_1 = '10.193.48.75'

local = configure_channel(local_ip)
remote_1 = configure_channel(remote_ip_1)
everybody = configure_channel(hosts=[(local_ip, 6379), (remote_ip_1, 6379)])

# Channels layer configuration
CHANNEL_LAYERS = {
    'server': local,
    'face': local,
    'coin': local,
    'dialog': local,
    'speech': local,
    'clock': everybody,
    'default': local,
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "coinCatalog/static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

import os

from .base import *

# static urls
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# static  locations
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# static root for productionalizing... do later
STATIC_ROOT = os.path.join(BASE_DIR, 'static_prod')

# database secrets
DB_NAME = os.environ.get(DB_NAME)
DB_USER = os.environ.get(DB_USER)
DB_PASSWORD = os.environ.get(DB_PASSWORD)
DB_HOST = os.environ.get(DB_HOST)
DB_PORT = os.environ.get(DB_PORT)

# database set up individually...
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# hosts
ALLOWED_HOSTS = []

# django settings
SECRET_KEY = os.environ.get('SECRET_KEY')

# weather api
WEATHERBIT_KEY = os.environ.get('WEATHERBIT_KEY')

# email api
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL= os.environ.get('FROM_EMAIL')


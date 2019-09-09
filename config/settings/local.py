from .base import *

from corsheaders.defaults import default_headers

DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = '5432'

CORS_ORIGIN_WHITELIST = (
    "http://localhost:8080",
)
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = ['*']
CORS_ALLOW_HEADERS = default_headers + (
    'access-control-allow-origin',
)

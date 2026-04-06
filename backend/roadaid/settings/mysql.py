# Import base settings for INSTALLED_APPS and all base config
from .base import *
# MySQL database settings for Django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'machnic',
        'USER': 'root',
        'PASSWORD': 'ramU0011@@',
        'HOST': 'db',  # Docker service name
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

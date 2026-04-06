"""
Development-specific settings.
"""
from .base import *

DEBUG = True

# Use SQLite for development if PostgreSQL is not available
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Use in-memory channel layer for development
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Celery - Use synchronous execution in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

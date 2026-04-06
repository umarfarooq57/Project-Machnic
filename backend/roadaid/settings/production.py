"""
Production-specific settings.
"""
import os
import sys
import warnings

from .base import *

DEBUG = False

# Warn if DEBUG is True in production and not on localhost
if DEBUG and not any(h in ALLOWED_HOSTS for h in ['localhost', '127.0.0.1']):
	warnings.warn('DEBUG is True in production! This is a security risk.', RuntimeWarning)

# Validate required secrets in production
required_env_vars = [
	'DJANGO_SECRET_KEY',
	'DB_NAME',
	'DB_USER',
	'DB_PASSWORD',
	'DB_HOST',
	'DB_PORT',
]
missing = [var for var in required_env_vars if not os.getenv(var)]
if missing:
	print(f"ERROR: Missing required environment variables in production: {', '.join(missing)}", file=sys.stderr)
	raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# PostgreSQL connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
	"https://yourdomain.com",
	"https://www.yourdomain.com",
]
CORS_ALLOW_CREDENTIALS = True

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Static and media files with S3/Cloudflare R2
INSTALLED_APPS += ['storages']

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', '')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', '')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN', '')
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_LOCATION = 'static'

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/' if AWS_S3_CUSTOM_DOMAIN else f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{AWS_LOCATION}/'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/' if AWS_S3_CUSTOM_DOMAIN else f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'

# Whitenoise fallback for static files (if S3 misconfigured)
try:
	assert AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME
except AssertionError:
	STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
	STATIC_URL = '/static/'
	MEDIA_URL = '/media/'

# Sentry integration
import sentry_sdk
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
	sentry_sdk.init(
		dsn=SENTRY_DSN,
		traces_sample_rate=0.5,
		environment='production',
	)

# settings_production.py
from .settings import *
import os
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ['*']  # Update with your actual domain

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here')

# Database - PostgreSQL for production
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///university.db',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'errors.log'),
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
}

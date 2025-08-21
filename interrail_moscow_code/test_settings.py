"""
Test settings for InterRail Moscow Code project.
This configuration uses SQLite for testing to avoid connecting to production database.
"""

from .settings import *

# Override database to use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for fastest tests
        # Alternative: Use file-based SQLite if you need to inspect test data
        # 'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Disable migrations for faster test execution
# Tests will create tables based on current models
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
DEBUG = False  # Always False in tests for security
SECRET_KEY = 'test-secret-key-only-for-testing'

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests (optional - uncomment if tests are too verbose)
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'null': {
#             'class': 'logging.NullHandler',
#         },
#     },
#     'root': {
#         'handlers': ['null'],
#     },
# }

# Media files for testing
MEDIA_ROOT = BASE_DIR / 'test_media'

# Static files
STATIC_ROOT = BASE_DIR / 'test_static'

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Celery (if you use it) - use synchronous execution in tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

print("🔧 Using test settings with SQLite in-memory database")
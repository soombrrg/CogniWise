from pathlib import Path

from environ import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))

environ.Env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "behaviors.apps.BehaviorsConfig",
    "rest_framework",
    "minio_storage",
    # projects app
    "main",
    "users",
    "orders",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "main.context_processors.user_avatar",  # caching user avatar
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"


# Database
DATABASES = {
    "default": {
        **env.db_url("DATABASE_URL"),
        "ATOMIC_REQUESTS": True,
        "OPTIONS": {
            "pool": True,
        },
    }
}
CACHES = {
    "default": env.cache_url("REDIS_URL"),
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files
USE_S3 = env("USE_S3", bool)
if USE_S3:
    STORAGES = {
        "default": {
            "BACKEND": "minio_storage.MinioMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "minio_storage.MinioStaticStorage",
        },
    }
    MINIO_STORAGE_ENDPOINT = env("MINIO_STORAGE_ENDPOINT")
    MINIO_STORAGE_ACCESS_KEY = env("MINIO_ROOT_USER")
    MINIO_STORAGE_SECRET_KEY = env("MINIO_ROOT_PASSWORD")
    MINIO_STORAGE_MEDIA_BUCKET_NAME = "local-media"
    MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
    MINIO_STORAGE_STATIC_BUCKET_NAME = "local-static"
    MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True
    MINIO_STORAGE_USE_HTTPS = env("MINIO_STORAGE_USE_HTTPS", bool)
    PROTOCOL = "https" if MINIO_STORAGE_USE_HTTPS else "http"

    STATIC_URL = (
        f"{PROTOCOL}://{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_STATIC_BUCKET_NAME}/"
    )
    STATIC_ROOT = BASE_DIR / "staticfiles"

    MEDIA_URL = (
        f"{PROTOCOL}://{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_MEDIA_BUCKET_NAME}/"
    )
    MEDIA_ROOT = BASE_DIR / "mediafiles"
else:
    STATIC_URL = "/staticfiles/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    MEDIA_URL = "mediafiles/"
    MEDIA_ROOT = BASE_DIR / "mediafiles"

STATICFILES_DIRS = [BASE_DIR / "static"]


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Custom Authentication
AUTH_USER_MODEL = "users.CustomUser"

LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "users:profile"
LOGOUT_REDIRECT_URL = "main:home"

# Security
SECURITY_MODE = env("SECURITY_MODE")
if SECURITY_MODE == "prod":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# Mailing
MAILING_MODE = env("MAILING_MODE")
# Testing Mailing
if MAILING_MODE == "test":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# SMTP Mailing
if MAILING_MODE == "prod":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env("EMAIL_PORT")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    if EMAIL_PORT == "587":
        EMAIL_USE_TLS = True
    if EMAIL_PORT == "465":
        EMAIL_USE_SSL = True

    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    SERVER_EMAIL = EMAIL_HOST_USER
    EMAIL_ADMIN = EMAIL_HOST_USER

# Yookassa keys
YOOKASSA_SHOP_ID = env("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = env("YOOKASSA_SECRET_KEY")
YOOKASSA_VAT_CODE = env("YOOKASSA_VAT_CODE")

# Initializing Yookassa
from yookassa import Configuration  # noqa

Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)


if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += (
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "debug_toolbar_force.middleware.ForceDebugToolbarMiddleware",
    )
    LOGGING = {
        "version": 1,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"django.db.backends": {"handlers": ["console"], "level": "DEBUG"}},
    }

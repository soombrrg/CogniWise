from pathlib import Path

from environ import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", cast=str, default="secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", cast=bool, default=False)

# ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
ALLOWED_HOSTS = ["*"]

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
    "cachalot",
    "storages",
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
USE_S3 = env("USE_S3", cast=bool, default=False)
if USE_S3:
    STORAGES = {
        "default": {
            "BACKEND": env(
                "DEFAULT_FILE_STORAGE",
                cast=str,
                default="django.core.files.storage.FileSystemStorage",
            ),
        },
        "staticfiles": {
            "BACKEND": env(
                "STATICFILES_STORAGE",
                cast=str,
                default="django.contrib.staticfiles.storage.StaticFilesStorage",
            ),
        },
    }

    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default=None)
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default=None)
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default=None)
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=None)
    AWS_S3_URL_PROTOCOL = env("AWS_S3_CUSTOM_DOMAIN_PROTOCOL", default="https:")

    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default=None)
    AWS_DEFAULT_ACL = env("AWS_DEFAULT_ACL", default="public-read")

    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False

    STATIC_URL = env("STATIC_URL", default="/local-static/")
    STATIC_ROOT = BASE_DIR / "staticfiles"
    MEDIA_URL = env("MEDIA_URL", default="/local-media/")
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
MAILING_MODE = env("MAILING_MODE", cast=str)
# Testing Mailing
if MAILING_MODE == "test":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# SMTP Mailing
if MAILING_MODE == "prod":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    EMAIL_HOST = env("EMAIL_HOST", cast=str)
    EMAIL_PORT = env("EMAIL_PORT", cast=int)
    EMAIL_HOST_USER = env("EMAIL_HOST_USER", cast=str)
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", cast=str)
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
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += (
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "debug_toolbar_force.middleware.ForceDebugToolbarMiddleware",
    )

    # Uncomment if app in docker
    # DEBUG_TOOLBAR_CONFIG = {
    #     "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    #     "RENDER_PANELS": True,
    # }

    # LOGGING = {
    #     "version": 1,
    #     "handlers": {"console": {"class": "logging.StreamHandler"}},
    #     "loggers": {"django.db.backends": {"handlers": ["console"], "level": "DEBUG"}},
    # }

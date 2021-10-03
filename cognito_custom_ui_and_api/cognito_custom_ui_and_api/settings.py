import os

from logging import Formatter
from pathlib import Path

from cognito_custom_ui_and_api.apps.core.apps import CoreConfig

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-c=%dkk#bxs_og2!=q@en!en)(412xa$oueg%8aofr!m*26ad=("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    CoreConfig.name,
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

ROOT_URLCONF = "webapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cognito_custom_ui_and_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Logging
# https://docs.djangoproject.com/en/3.1/topics/logging/


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": Formatter,
            "format": "%(asctime)s - level=%(levelname)s - %(name)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "": {"level": os.getenv("ROOT_LOG_LEVEL", "INFO"), "handlers": ["console"]},
        "cognito_custom_ui_and_api": {
            "level": os.getenv("PROJECT_LOG_LEVEL", "DEBUG"),
            "handlers": ["console"],
            "propagate": False,
        },
        "django": {"level": os.getenv("DJANGO_LOG_LEVEL", "INFO"), "handlers": ["console"]},
        "django.db.backends": {"level": os.getenv("DJANGO_DB_BACKENDS_LOG_LEVEL", "INFO"), "handlers": ["console"]},
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#####
# Custom settings for Cognito

AWS_COGNITO_USER_POOL_ID = "us-east-1_LyI6GnFWu"
AWS_COGNITO_REGION = AWS_COGNITO_USER_POOL_ID.split("_")[0]
AWS_COGNITO_APP_CLIENT_ID = "3hdisk9m7qnvooiqfpv3ijetpg"
AWS_COGNITO_APP_CLIENT_SECRET = "e4c1qakgdt5bjfev9pv4nfcedr1gg3u5e6ai7d11vnh1mojm3d8"
AWS_COGNITO_SERVICE_ACCOUNT_ACCESS_KEY = "AKIAXAQEEUDOH4LPY7WJ"
AWS_COGNITO_SERVICE_ACCOUNT_ACCESS_SECRET = "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"

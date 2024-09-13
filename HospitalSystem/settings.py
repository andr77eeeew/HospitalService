"""
Django settings for HospitalSystem project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from datetime import timedelta
from pathlib import Path
from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    # Время жизни access токена (чаще всего это 5-15 минут)
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),

    # Время жизни refresh токена (чаще всего это 1 день или больше)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    # Время жизни токена для подтверждения (для использования с функцией "обновить пароль" или другими подтверждениями)
    'ROTATE_REFRESH_TOKENS': True,  # Автоматически обновляет refresh токен при использовании

    # Удаление старого refresh токена при обновлении (защита от утечки)
    'BLACKLIST_AFTER_ROTATION': True,  # Добавляет старый refresh токен в черный список после ротации

    # Защита от повторного использования refresh токена
    'UPDATE_LAST_LOGIN': True,  # Обновляет поле последнего входа при успешном использовании токена

    # Аутентификационный заголовок (используется Bearer токен)
    'AUTH_HEADER_TYPES': ('Bearer',),

    # Аутентификация с использованием Cookies (например, для безопасных приложений)
    'AUTH_COOKIE': 'access_token',  # Имя cookie для хранения access токена
    'AUTH_COOKIE_REFRESH': 'refresh_token',  # Имя cookie для хранения refresh токена
    'AUTH_COOKIE_SECURE': False,  # Включение secure флага для передачи cookie только по HTTPS
    'AUTH_COOKIE_HTTP_ONLY': True,  # Защита от доступа к cookie через JavaScript
    'AUTH_COOKIE_PATH': '/',  # Путь для доступа к cookie
    'AUTH_COOKIE_SAMESITE': 'Lax',  # Политика SameSite (может быть 'Lax', 'Strict', 'None')

    # Алгоритм кодирования токенов (по умолчанию HS256, но можно выбрать RS256 для использования с ключами)
    'ALGORITHM': 'HS256',

    # Секретный ключ (используется для кодирования токенов, должен быть достаточно надежным)
    'SIGNING_KEY': SECRET_KEY,  # Ваш Django SECRET_KEY

    # Удаление токена при его недействительности
    'VERIFYING_KEY': None,

    # Логирование доступа через JWT
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),

    # Разрешение использования JTI claim для защиты от повторного использования токенов
    'JTI_CLAIM': 'jti',

    # Признак субъекта токена (уникальный идентификатор пользователя)
    'USER_ID_FIELD': 'id',  # Поле модели, используемое в качестве ID пользователя

    # Название поля, используемого для хранения идентификатора пользователя в токене
    'USER_ID_CLAIM': 'id',

    # Включение blacklisting
    'TOKEN_BLACKLIST_ENABLED': True,  # Активация системы черного списка токенов

    # Опциональные настройки для OAuth2 (если используется)
    'AUTH_COOKIE_DOMAIN': None,  # Домен для доступа к cookie (если используется несколько доменов)

    # Настройки для работы с часами (выполнение проверки времени жизни токена)
    'LEEWAY': 0,  # Допустимая погрешность времени (например, для серверов с разными часами)
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'HospitalSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'HospitalSystem.wsgi.application'

ASGI_APPLICATION = 'HospitalSystem.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('NAME'),
        'USER': env.str('USER'),
        'PASSWORD': env.str('PASSWORD'),
        'HOST': env.str('HOST'),
        'PORT': env.int('PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost:5173',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    'Accept',
    'Origin',
    'Access-Control-Request-Method',
    'Access-Control-Request-Headers',
    'HTTP_AUTHORIZATION',
)


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATIC_URL = '/static/'


MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

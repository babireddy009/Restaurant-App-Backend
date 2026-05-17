import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-restaurant-dev-key-change-in-prod')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ─── Daphne MUST be before everything for WebSockets, Jazzmin before admin ─
INSTALLED_APPS = [
    'daphne',
    'jazzmin',                              # ← FIRST
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    # Local apps
    'accounts',
    'menu',
    'orders',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600, # Database connection pooling
    }
}

# Use remote database if DATABASE_URL is provided in .env or Hosting Platform
database_url = os.getenv("DATABASE_URL")
if database_url:
    DATABASES['default'] = dj_database_url.parse(database_url, conn_max_age=600)

# Caching Configuration
# For production at 100k scale, switch this to Redis Cache using django-redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'restaurant-cache',
    }
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:5174,http://localhost:3000,https://restaurant-app-frontend-n4mn-o0746ezp2.vercel.app'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# CSRF Settings
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'https://msrrayalaseemaruchulu.com,https://www.msrrayalaseemaruchulu.com'
).split(',')

# Razorpay
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

# ─────────────────────────────────────────────────────────────────────────────
# JAZZMIN — Beautiful Admin UI Configuration
# ─────────────────────────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    # ── Branding ──────────────────────────────────────────────────────────
    "site_title":        "MSR Admin",
    "site_header":       "MSR Rayalasema Ruchulu",
    "site_brand":        "MSR Ruchulu",
    "welcome_sign":      "Welcome to MSR Rayalasema Ruchulu Management",
    "copyright":         "MSR Rayalasema Ruchulu © 2024",
    "site_icon":         None,
    "site_logo":         None,

    # ── Search ────────────────────────────────────────────────────────────
    "search_model": ["accounts.CustomUser", "menu.MenuItem", "orders.Order"],
    "topmenu_links": [
        {"name": "🏠 Home",        "url": "admin:index"},
        {"name": "📋 Menu Items",  "model": "menu.MenuItem"},
        {"name": "🛒 Orders",      "model": "orders.Order"},
        {"name": "👥 Customers",   "model": "accounts.CustomUser"},
        {"name": "🌐 View Site",   "url": "/", "new_window": True},
    ],

    # ── User menu (top right) ──────────────────────────────────────────
    "usermenu_links": [
        {"name": "🌐 Front End",  "url": "http://localhost:5173", "new_window": True},
        {"name": "⚙️  Profile",   "url": "admin:accounts_customuser_change", "icon": "fas fa-user"},
    ],

    # ── Sidebar Icons (Font Awesome 5) ────────────────────────────────
    "icons": {
        "auth":                     "fas fa-users-cog",
        "accounts.CustomUser":      "fas fa-user-circle",
        "menu.Category":            "fas fa-th-large",
        "menu.MenuItem":            "fas fa-utensils",
        "orders.Order":             "fas fa-shopping-bag",
        "orders.OrderItem":         "fas fa-list",
        "payments.Payment":         "fas fa-credit-card",
    },
    "default_icon_parents":  "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # ── Sidebar layout ─────────────────────────────────────────────────
    "show_sidebar":             True,
    "navigation_expanded":      True,
    "hide_apps":                [],
    "hide_models":              [],
    "order_with_respect_to": [
        "orders", "menu", "payments", "accounts",
    ],

    # ── Custom sidebar menu ────────────────────────────────────────────
    "custom_links": {
        "orders": [
            {
                "name": "📊 Pending Orders",
                "url":  "admin:orders_order_changelist",
                "icon": "fas fa-clock",
                "permissions": ["orders.view_order"],
            },
        ],
    },

    # ── Change list UI ─────────────────────────────────────────────────
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user":  "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,

    # ── Related modal popup instead of new page ────────────────────────
    "related_modal_active": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text":    False,
    "footer_small_text":    False,
    "body_small_text":      False,
    "brand_small_text":     False,

    # ── Color Theme ───────────────────────────────────────────────────
    "brand_colour":         "navbar-orange",
    "accent":               "accent-orange",
    "navbar":               "navbar-dark navbar-orange",
    "no_navbar_border":     True,
    "navbar_fixed":         True,
    "layout_boxed":         False,
    "footer_fixed":         False,
    "sidebar_fixed":        True,
    "sidebar":              "sidebar-dark-orange",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,

    # ── Theme ─────────────────────────────────────────────────────────
    "theme":                "darkly",       # dark professional look
    "dark_mode_theme":      "darkly",
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
}

# Email Backend Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')


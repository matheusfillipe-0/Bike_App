from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-2ft$9*znz!rxbhbi39nhd2-9oaugw@nxki63t-g1b+$on=td^l'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'bikes',
      
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'controle_bike',   
        'USER': 'user_matheus',       
        'PASSWORD': '102900',    
        'HOST': 'localhost',    
        'PORT': '5432',           
    }
}
 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     

]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'bike_rental_system.urls'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  


WSGI_APPLICATION = 'bike_rental_system.wsgi.application'

 
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
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
   
]
 

CSRF_COOKIE_SECURE = True  


LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Maceio'

AUTHENTICATION_BACKENDS = (
    
    'django.contrib.auth.backends.ModelBackend', )
 
 

 
AUTH_USER_MODEL = 'bikes.Usuario'  

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  
        ],
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

USE_I18N = True

USE_TZ = True
 
STATICFILES_DIRS = [
    BASE_DIR / 'bikes' / 'static',  
]

STATIC_URL = '/static/'  


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

LOGIN_REDIRECT_URL = 'home'

LOGIN_URL = '/login/' 
 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

 
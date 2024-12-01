 
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bike_rental_system.settings')


application = get_wsgi_application()

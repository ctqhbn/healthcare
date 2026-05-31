import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcare.settings")

from healthcare.wsgi import application

app = application

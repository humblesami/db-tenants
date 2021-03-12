from django.apps import AppConfig
from django.conf import settings


class DjUtilsConfig(AppConfig):
    name = 'dj_utils'
    settings.VAR1 = 788
    print(settings.DEBUG)
    print(settings.VAR1)

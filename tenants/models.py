# from django.contrib.auth.models import User
from django.contrib.auth.models import User

from django.db import models
from django.db import connection
from django.conf import settings


class TenantManager(models.Manager):
    def get_queryset(self):
        current_db = connection.settings_dict['NAME']
        res = []
        if current_db == settings.DATABASES['default']['NAME']:
            res = super().get_queryset().filter(active=True)
        return res


class Tenant(models.Model):
    objects = TenantManager()

    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class GlobalUser(User):
    tenants = models.ManyToManyField(Tenant, related_name='users')

    def save(self, *args, **kwargs):
        super().save(args, kwargs)

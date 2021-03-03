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

    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='tenants')

    def __str__(self):
        return self.name


tenant_app_choices = []
for app_name in settings.TENANT_APPS:
    tenant_app_choices.append((app_name, app_name))


class TenantApp(models.Model):
    name = models.CharField(choices=tenant_app_choices, max_length=200)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='apps')

    def __str__(self):
        return self.name


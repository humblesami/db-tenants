from django.db import models
from django.db import connection


class TenantManager(models.Manager):
    def get_queryset(self):
        current_db = connection.settings_dict['NAME']
        res = []
        if current_db == 'default':
            res = super().get_queryset().filter(active=True)
        return res


class Tenant(models.Model):
    objects = TenantManager()

    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

from django.contrib.auth.models import User
from django.db import models

from django.contrib.admin import AdminSite

original_get_app_list = AdminSite.get_app_list


class AdminSiteExtension(AdminSite):
    def get_app_list(self, request):
        app_list = original_get_app_list(self, request)
        for app in app_list:
            app['name'] = app['name']
        return app_list


AdminSite.get_app_list = AdminSiteExtension.get_app_list


class DefaultClass(models.Model):
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_query_name='%(app_label)s_%(class)s_created_by',
        related_name='%(app_label)s_%(class)s_created_by'
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='%(app_label)s_%(class)s_updated_by',
        related_query_name='%(app_label)s_%(class)s_updated_by'
    )

    class Meta:
        abstract = True

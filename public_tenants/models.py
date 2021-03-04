# from django.contrib.auth.models import User
import importlib
from django.core.management import call_command
from django.db import models
from django.db import connection
from django.conf import settings
from django.contrib.auth.models import User
#from django.contrib.auth import get_user_model
#User = get_user_model()

from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_delete

import tenant_arguments
from dj_utils import methods
from .thread_local import THREAD_LOCAL



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
    owner_email = models.CharField(max_length=200, null=True)
    subscription = models.ForeignKey('public_tenant_management.Subscription', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        creating = False
        if not self.pk:
            creating = True
        res = super().save()
        if creating:
            client_name = self.name
            email = self.owner_email

            app_names = []
            if self.subscription:
                app_names = self.subscription.package.products.values_list('name', flat=True)
                for app_name in app_names:
                    TenantApp.objects.create(tenant_id=self.pk, name=app_name)
            else:
                app_names = self.apps.values_list('name', flat=True)

            tenant_arguments.db_to_create = client_name
            importlib.import_module('tenant_create_db')

            tenant = Tenant.objects.create(name=client_name)
            user = User.objects.filter(email=email)
            if user:
                user = user[0]
            else:
                user = User(
                    email=email, username=email,
                    is_active=True
                )
                user.save()
                user.set_password('123')  # replace with your real password
                user.save()

            tenant.users.add(user)
            tenant.save()

            if not settings.DATABASES.get(client_name):
                default_config = settings.DATABASES['default']
                new_config = default_config.copy()
                new_config['NAME'] = client_name
                settings.DATABASES[client_name] = new_config

            call_command('new_tenant', name=client_name, apps=app_names)
            setattr(THREAD_LOCAL, "DB", client_name)
            user = User(
                email=email, username=email,
                last_login=methods.now_str(),
                is_active=True, is_staff=True, is_superuser=True
            )
            user.save()
            user.set_password('123')
            user.save()
            setattr(THREAD_LOCAL, "DB", 'default')
        return res


@receiver(pre_delete)
def delete_repo(sender, instance, **kwargs):
    if type(instance) == Tenant:

        try:
            db_name = instance.name
            tenant_arguments.db_to_drop = db_name
            importlib.import_module('tenant_drop_db')
            a = 1
        except:
            message = methods.get_error_message()
            a = 1


tenant_app_choices = []
for app_name in settings.TENANT_APPS:
    tenant_app_choices.append((app_name, app_name))


class TenantApp(models.Model):
    name = models.CharField(choices=tenant_app_choices, max_length=200)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='apps')

    def __str__(self):
        return self.name


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

    name = models.CharField(max_length=100, unique=True, blank=True)
    active = models.BooleanField(default=True)
    owner_email = models.CharField(max_length=200, blank=True, null=True)
    users = models.ManyToManyField(User, related_name='tenants', blank=True)
    subscription = models.ForeignKey('public_tenant_management.Subscription', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        creating = False
        if not self.pk:
            creating = True

        owner = None
        app_names = []
        client_name = self.name
        email = self.owner_email
        if self.subscription:
            app_names = self.subscription.package.products.values_list('name', flat=True)
            email = self.subscription.client.email
            self.owner_email = email
            client_name = self.subscription.client.name
            self.name = client_name
        else:
            app_names = self.apps.values_list('name', flat=True)
            if self.users.count():
                owner = self.users[0]
                email = owner.email

        if not self.name:
            raise ValueError('Invalid name')
        res = super().save()
        if creating:
            if self.subscription:
                for app_name in app_names:
                    tenant_app = TenantApp(name=app_name, tenant_id=self.pk)
                    tenant_app.save()
            tenant_arguments.db_to_create = client_name
            try:
                importlib.import_module('tenant_create_db')
            except:
                message = methods.get_error_message()
                if 'already exist' in message:
                    pass
                else:
                    raise

            if not owner:
                owner = User.objects.filter(email=email)
                if owner:
                    owner = owner[0]
            if not owner:
                owner = User.objects.filter(email=email).first()
                if not owner:
                    owner = User(
                        email=email, username=email,
                        is_active=True
                    )
                    owner.save()
                    owner.set_password('123')  # replace with your real password
                    owner.save()

            if not self.users.count():
                self.users.add(owner)
                self.save()

            if not settings.DATABASES.get(client_name):
                default_config = settings.DATABASES['default']
                new_config = default_config.copy()
                new_config['NAME'] = client_name
                settings.DATABASES[client_name] = new_config

            call_command('new_tenant', name=client_name, apps=app_names)
            setattr(THREAD_LOCAL, "DB", client_name)
            super_tenant_user = User.objects.filter(email=email).first()
            if not super_tenant_user:
                super_tenant_user = User(
                    email=email, username=email,
                    last_login=methods.now_str(),
                    is_active=True, is_staff=True, is_superuser=True
                )
                super_tenant_user.save()
            else:
                super_tenant_user.is_active = True
                super_tenant_user.is_staff = True
                super_tenant_user.is_superuser = True
            super_tenant_user.set_password('123')
            super_tenant_user.save()
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
            raise


tenant_app_choices = []
for app_name in settings.TENANT_APPS:
    tenant_app_choices.append((app_name, app_name))


class TenantApp(models.Model):
    name = models.CharField(choices=tenant_app_choices, max_length=200)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='apps')

    class Meta:
        unique_together = (('name', 'tenant'),)

    def __str__(self):
        return self.name



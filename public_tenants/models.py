# from django.contrib.auth.models import User
from django.db import models
from django.db import connection
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models.signals import pre_delete


import importlib
import tenant_arguments
from dj_utils import methods
from public_tenants.middlewares import THREAD_LOCAL


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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    users = models.ManyToManyField(User, related_name='tenants', blank=True)
    subscription = models.ForeignKey('public_tenant_management.Subscription', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        creating = False
        if not self.pk:
            creating = True

        app_names = []
        if self.subscription:
            self.owner = self.subscription.client.related_user
            app_names = self.subscription.package.products.values_list('name', flat=True)
            self.name = self.subscription.db
        else:
            app_names = self.apps.values_list('name', flat=True)
            if self.users.count():
                self.owner = self.users[0]
        res = super().save()
        if creating:
            if self.subscription:
                for app_name in app_names:
                    tenant_app = TenantApp(name=app_name, tenant_id=self.pk)
                    tenant_app.save()
            tenant_arguments.db_to_create = self.name
            try:
                importlib.import_module('tenant_create_db')
            except:
                message = methods.get_error_message()
                if 'already exist' in message:
                    pass
                else:
                    raise

            if not self.owner:
                raise ValueError('Invalid owner')

            if not settings.DATABASES.get(self.name):
                default_config = settings.DATABASES['default']
                new_config = default_config.copy()
                new_config['NAME'] = self.name
                settings.DATABASES[self.name] = new_config

            call_command('new_tenant', name=self.name, apps=app_names)
            self.add_users_to_new_db()
            setattr(THREAD_LOCAL, "DB", 'default')
        return res

    def add_users_to_new_db(self):
        new_db = self.name
        email = self.owner.email
        tenant_users = self.users.all().values_list('email', flat=True)

        setattr(THREAD_LOCAL, "DB", new_db)
        db = connection.settings_dict['NAME']

        super_tenant_user = User(
            email=email, username=email,
            last_login=methods.now_str(),
            is_active=True, is_staff=True, is_superuser=True
        )
        super_tenant_user.save()
        db = connection.settings_dict['NAME']
        for user in tenant_users:
            if user['email'] == super_tenant_user.email:
                continue
            staff_user = User(
                email=user['email'], username=user['email'],
                last_login=methods.now_str(),
                is_active=True, is_staff=True
            )
            staff_user.save()
            db = connection.settings_dict['NAME']
            a = 1


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



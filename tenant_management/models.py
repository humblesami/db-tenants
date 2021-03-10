# from django.contrib.auth.models import User
from django.db import models, transaction
from django.db import connection
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models.signals import post_save, post_delete


import importlib
import tenant_arguments
from dj_utils import methods
from tenant_management.change_db import set_db_for_router


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

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        creating = False
        if not self.pk:
            creating = True
            self.get_owner()

        if not self.name:
            raise ValueError('Name cannot be blank')
        if not self.owner:
            raise ValueError('Name cannot be blank')
        res = super().save()
        if creating:
            app_names = self.get_apps()
            self.create_tenant(app_names)
        return res

    def get_apps(self):
        app_names = settings.TENANT_APPS
        return app_names

    def get_owner(self):
        pass

    def create_tenant(self, app_names):
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
        try:
            self.add_users_to_new_db()
        except:
            message = methods.get_error_message()
            a = 1
        set_db_for_router('')

    def add_users_to_new_db(self):
        new_db = self.name
        email = self.owner.email
        tenant_users = list(self.users.all().values('email'))

        set_db_for_router(new_db)
        super_tenant_user = User(
            email=email, username=email,
            last_login=methods.now_str(),
            is_active=True, is_staff=True, is_superuser=True
        )
        super_tenant_user.set_password('123')
        super_tenant_user.save()
        for user in tenant_users:
            if user['email'] == super_tenant_user.email:
                continue
            staff_user = User(
                email=user['email'], username=user['email'],
                last_login=methods.now_str(),
                is_active=True, is_staff=True
            )
            staff_user.set_password('123')
            staff_user.save()
            a = 1


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


def add_owner_to_users(instance):
    if not instance.users.all():
        instance.users.add(instance.owner)


def on_tenant_saved(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: add_owner_to_users(instance))


def drop_db(sender, instance, **kwargs):
    db_name = instance.name
    tenant_arguments.db_to_drop = db_name
    importlib.import_module('tenant_drop_db')


post_save.connect(on_tenant_saved, sender=Tenant)
post_delete.connect(drop_db, sender=Tenant)

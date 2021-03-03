import importlib
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from public_customers.models import Client
from dj_utils.models import DefaultClass

from dj_utils import methods
from public_tenants.middlewares import THREAD_LOCAL
from public_tenants.models import Tenant, TenantApp


class PackageType(DefaultClass):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


tenant_app_choices = []
for app_name in settings.TENANT_APPS:
    tenant_app_choices.append((app_name, app_name))


class Product(DefaultClass):
    name = models.CharField(choices=tenant_app_choices, max_length=200)

    def __str__(self):
        return self.name


class Package(DefaultClass):
    class Meta:
        pass

    name= models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    package_type = models.ForeignKey(PackageType, on_delete=models.CASCADE, related_name='packages', null=True)
    price = models.IntegerField()
    valid_for_months = models.IntegerField(default=1)
    products = models.ManyToManyField(Product, related_name='packages')

    def __str__(self):
        return self.name


class Subscription(DefaultClass):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    connection_charges = models.IntegerField(default=0)
    connection_date = models.DateField()
    expiry_date = models.DateField(null=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.client.name + '-' + self.package.name

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.active = False
        res = super().save()
        try:
            if self.active:
                super_user = User.objects.filter(email=self.client.email)
                if not super_user:
                    try:
                        importlib.import_module('create_db')
                    except:
                        message = methods.get_error_message()
                        a = 1
                    apps = self.package.products.values_list('name', flat=True)
                    self.__class__.create_tenant(self.client.name, self.client.email, apps)
        except:
            message = methods.get_error_message()
            self.active = False
        return res

    @classmethod
    def create_tenant(cls, client_name, email, apps):
        tenant = Tenant.objects.create(name=client_name)
        tenant_id = tenant.id

        for app_name in apps:
            app = TenantApp(name=app_name, tenant_id=tenant_id)
            app.save()

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

        call_command('new_tenant', name=client_name, apps=apps)
        setattr(THREAD_LOCAL, "DB", client_name)
        user = User(
            email=email, username=email,
            last_login=methods.now_str(),
            is_active=True, is_staff=True, is_superuser=True
        )
        user.save()
        user.set_password('123')  # replace with your real password
        user.save()
        setattr(THREAD_LOCAL, "DB", 'default')


class Payment(DefaultClass):
    class Meta:
        pass

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    due_amount = models.IntegerField(default=0, verbose_name='Due Amount')
    amount = models.IntegerField()
    payment_date = models.DateField()
    renewal_start_date = models.DateField()
    renewal_end_date = models.DateField()

    def __str__(self):
        return '{}-{}'.format(self.subscription.__str__(), self.amount)

    amount_error = None

    def save(self, *args, **kwargs):
        renewal_start_date = self.renewal_start_date or self.payment_date
        to_be_paid = self.subscription.price

        # in case of first subscription or subscription after service terminated
        customer_balance = self.subscription.client.balance or 0
        if (not self.subscription.active) or (len(self.subscription.payments) <= 1):
            to_be_paid += self.subscription.connection_charges

        if self.subscription.active:
            last_obj = Payment.objects.filter(subscription_id=self.subscription.id).order_by('renewal_end_date').last()
            if len(last_obj):
                if last_obj.renewal_end_date > self.renewal_start_date:
                    diff_days = methods.get_days_difference(last_obj.renewal_start_date, last_obj.renewal_end_date)
                    renewal_start_date = methods.add_days(last_obj.renewal_start_date, diff_days)

        balance = self.subscription.client.balance or 0
        being_paid = self.amount

        self.due_amount = to_be_paid
        if self.pk:
            last_payment = Payment.objects.filter(id=self.pk)[0]
            being_paid -= last_payment.amount
            to_be_paid -= last_payment.due_amount

        customer_balance = customer_balance + being_paid - to_be_paid

        self.subscription.client.balance = customer_balance
        self.subscription.client.save()
        self.renewal_start_date = renewal_start_date
        renewal_end_date = methods.add_one_month_to_date(renewal_start_date)
        self.renewal_end_date = renewal_end_date
        self.subscription.expiry_date = renewal_end_date

        res = super().save(args, kwargs)
        self.subscription.save()
        return res



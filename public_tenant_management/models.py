from django.db import models
from public_customers.models import Client
from dj_utils.models import DefaultClass
from dj_utils import methods


class PackageType(DefaultClass):
    name = models.CharField(max_length=200)

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
        res = super().save(args, kwargs)
        return res


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
                    diff_days = get_days_difference(last_obj.renewal_start_date, last_obj.renewal_end_date)
                    renewal_start_date = add_days(last_obj.renewal_start_date, diff_days)

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
        renewal_end_date = add_one_month_to_date(renewal_start_date)
        self.renewal_end_date = renewal_end_date
        self.subscription.expiry_date = renewal_end_date

        res = super().save(args, kwargs)
        self.subscription.save()
        return res


def add_months(source_date, months):
    res = methods.add_interval('months', months, source_date)
    return res


def add_one_month_to_date(given_date):
    given_date = methods.add_interval('days', -1, given_date)
    return add_months(given_date, 1)


def get_days_difference(start_date, end_date):
    seconds = methods.dt_span_seconds(start_date, end_date)
    days = seconds / 60 / 60 / 24
    days = round(days)
    return days


def add_days(dt1, days):
    res = methods.add_interval('days', days, dt1)
    return res

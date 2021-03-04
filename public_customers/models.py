from django.db import models
from dj_utils.models import DefaultClass


class AreaManager(models.Manager):
    def get_queryset(self):
        res = super().get_queryset().filter(active=True)
        return res


class AreaManagerAll(models.Manager):
    def get_queryset(self):
        res = super().get_queryset()
        return res


class Area(DefaultClass):
    class Meta:
        ordering = ('-active', 'name', 'created_at')

    objects = AreaManager()
    full = AreaManagerAll()
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True, null=True)

    def __str__(self):
        return self.name


class Client(DefaultClass):
    name = models.CharField(max_length=200)
    area = models.ForeignKey(Area, related_name='clients', null=True, blank=True, on_delete=models.CASCADE)

    father_name = models.CharField(max_length=200, null=True, blank=True)
    mobile = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200)
    cnic = models.CharField(max_length=200, unique=True, null=True, blank=True)
    address = models.CharField(max_length=1024, null=True, blank=True)
    # balance is here...

    balance = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        ordering = ('area', 'name')
        pass
        # verbose_name_plural = 'Sami'

    def __str__(self):
        return self.name

    def is_defaulter(self):
        pass

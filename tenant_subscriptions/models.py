from django.db import models
from tenant_management import models as tenant_models
from package_subscriptions.models import Subscription


class Tenant(tenant_models.Tenant):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)

    def get_apps(self):
        if self.subscription:
            return self.subscription.package.products.values_list('name', flat=True)
        else:
            return super().get_apps()

    def get_owner(self):
        if self.subscription:
            self.owner = self.subscription.client.related_user
            self.name = self.subscription.db


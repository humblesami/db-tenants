from django.contrib.auth.models import User

from django.db import models
from django.db import connection
from public_tenants.models import GlobalUser, Tenant


class TenantUser(User):
    def save(self, *args, **kwargs):
        user_obj = GlobalUser.objects.create(username=self.username, )
        super().save(args, kwargs)
        current_db = connection.settings_dict['NAME']
        current_tenant = Tenant.objects.filter(name=current_db)
        if current_tenant:
            current_tenant = current_tenant[0]
        user_obj.tenants.add(current_tenant)
        user_obj.save()
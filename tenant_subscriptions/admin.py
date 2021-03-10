from django.contrib import admin
from tenant_management.models import TenantApp
from .models import Tenant


class TenantAppInlineAdmin(admin.StackedInline):
    model = TenantApp


class TenantAdmin(admin.ModelAdmin):
    inlines = (TenantAppInlineAdmin,)


admin.site.register(Tenant, TenantAdmin)

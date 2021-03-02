from django.contrib import admin
from public_tenants.models import Tenant, TenantApp


class TenantAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant')


admin.site.register(Tenant)
admin.site.register(TenantApp, TenantAppAdmin)

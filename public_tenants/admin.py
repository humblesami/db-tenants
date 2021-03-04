from django.contrib import admin
from public_tenants.models import Tenant, TenantApp


class TenantAppInlineAdmin(admin.StackedInline):
    list_display = ('name', 'tenant')
    model = TenantApp


class TenantAdmin(admin.ModelAdmin):
    inlines = (TenantAppInlineAdmin,)


admin.site.register(Tenant, TenantAdmin)

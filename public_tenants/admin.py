from django.contrib import admin
from public_tenants.models import Tenant, TenantApp


class TenantAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant')


class TenantAppInlineAdmin(admin.StackedInline):
    model = TenantApp


class TenantAdmin(admin.ModelAdmin):
    inlines = (TenantAppInlineAdmin,)


admin.site.register(Tenant, TenantAdmin)
admin.site.register(TenantApp, TenantAppAdmin)

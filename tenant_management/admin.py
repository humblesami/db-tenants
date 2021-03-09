from django.contrib import admin
from tenant_management.models import Tenant, TenantApp


class TenantAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant')


class TenantAppInlineAdmin(admin.StackedInline):
    model = TenantApp


class TenantAdmin(admin.ModelAdmin):
    inlines = (TenantAppInlineAdmin,)


admin.site.register(Tenant, TenantAdmin)
admin.site.register(TenantApp, TenantAppAdmin)

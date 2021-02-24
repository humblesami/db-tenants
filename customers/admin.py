from django.contrib import admin
from .models import Area, Client

# Register your models here.
from dj_utils.admin import ParentModelAdmin


class AreaAdmin(ParentModelAdmin):
    list_display = ['name', 'active', 'created_at']
    search_fields = ['name']
    list_filter = ['active']

    def get_queryset(self, request):
        qs = Area.full.all()
        return qs


class ClientAdmin(ParentModelAdmin):
    list_display = ['area', 'name','mobile','email', 'balance']
    search_fields = ['name', 'email', 'mobile', 'area']
    fields = ['area', 'name','mobile','email', 'cnic', 'balance']
    readonly_fields = ['balance', 'created_at', 'updated_at', 'created_by', 'updated_by']
    autocomplete_fields = ['area']


admin.site.register(Area, AreaAdmin)
admin.site.register(Client, ClientAdmin)

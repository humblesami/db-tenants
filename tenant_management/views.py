from django.conf import settings
from django.http import JsonResponse

from tenant_management.middlewares import set_db_for_router
from tenant_management.models import Tenant, TenantApp


def get_all_apps(request):
    host_name = request.get_host().split(":")[0].lower()
    arr = host_name.split('.')
    if arr:
        if len(arr):
            host_name = arr[0]
    set_db_for_router('')
    tenant = Tenant.objects.filter(name=host_name)
    tenant_apps = []
    apps = {
        'shared_apps': settings.SHARED_APPS,
        'public_apps': settings.PUBLIC_APPS
    }
    if tenant:
        tenant = tenant[0]
        tenant_apps = TenantApp.objects.filter(tenant_id=tenant.id)
        tenant_apps = tenant_apps.values_list('name', flat=True)
        tenant_apps = list(tenant_apps)
    apps['tenant_apps'] = tenant_apps
    res = {'data': apps, 'status': 'success' }
    res = JsonResponse(res)
    return res

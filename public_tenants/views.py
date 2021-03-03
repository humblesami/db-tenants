from django.http import JsonResponse
from public_tenants.middlewares import THREAD_LOCAL
from public_tenants.models import Tenant, TenantApp


def get_tenant_apps(request):
    host_name = request.get_host().split(":")[0].lower()
    arr = host_name.split('.')
    if arr:
        if len(arr):
            host_name = arr[0]
    setattr(THREAD_LOCAL, "DB", 'default')
    tenant = Tenant.objects.filter(name=host_name)
    apps = []
    if tenant:
        tenant = tenant[0]
        apps = TenantApp.objects.filter(tenant_id=tenant.id)
        apps = apps.values_list('name', flat=True)
        apps = list(apps)
    res = {'data': apps, 'status': 'success' }
    res = JsonResponse(res)
    return res

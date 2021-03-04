from django.conf import settings
from django.db import connection
from .models import Tenant
from .thread_local import THREAD_LOCAL


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_db = connection.settings_dict['NAME']
        host_name = request.get_host().split(":")[0].lower()
        arr = host_name.split('.')
        if arr:
            if len(arr):
                host_name = arr[0]
        default_config = settings.DATABASES['default']
        shared_db = default_config['NAME']
        if current_db != shared_db:
            setattr(THREAD_LOCAL, "DB", shared_db)
        hosts = Tenant.objects.filter(name=host_name)
        try:
            if hosts:
                host_name = hosts[0].name
                if not settings.DATABASES.get(host_name):
                    tenant_config = default_config.copy()
                    tenant_config['NAME'] = host_name
                    settings.DATABASES[host_name] = tenant_config
                setattr(THREAD_LOCAL, "DB", host_name)
            else:
                if current_db != shared_db:
                    setattr(THREAD_LOCAL, "DB", shared_db)
        except:
            pass
        response = self.get_response(request)
        return response


def get_current_db_name():
    return getattr(THREAD_LOCAL, "DB", None)


def set_db_for_router(db):
    setattr(THREAD_LOCAL, "DB", db)

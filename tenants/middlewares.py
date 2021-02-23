import threading
from uuid import uuid4

from django.db import connection

from .models import Tenant
from .utils import tenant_db_from_request

THREAD_LOCAL = threading.local()


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
        if current_db != 'default':
            setattr(THREAD_LOCAL, "DB", 'default')
        hosts = Tenant.objects.filter(name=host_name)
        try:
            if hosts:
                host_name = hosts[0].name
                setattr(THREAD_LOCAL, "DB", host_name)
            else:
                if current_db != 'default':
                    setattr(THREAD_LOCAL, "DB", 'default')
        except:
            pass
        response = self.get_response(request)
        return response


def get_current_db_name():
    return getattr(THREAD_LOCAL, "DB", None)


def set_db_for_router(db):
    setattr(THREAD_LOCAL, "DB", db)

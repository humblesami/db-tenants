from django.conf import settings
from django.db import connection
from dj_utils.methods import get_error_message

from public_tenants.models import Tenant
from public_tenants.change_db import set_db_for_router


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_db = connection.settings_dict['NAME']
        sub_domain = request.get_host().split(":")[0].lower()
        arr = sub_domain.split('.')
        host_name = ''
        if arr:
            if len(arr):
                host_name = arr[0]
                if not host_name:
                    return
                if current_db == host_name:
                    return
        not_local = (not host_name.startswith('localhost')) and (not host_name.startswith('127'))
        if host_name and not_local:
            if current_db != host_name:
                default_config = settings.DATABASES['default']
                shared_db = default_config['NAME']
                if current_db != shared_db:
                    set_db_for_router(shared_db, default_config)
                try:
                    hosts = list(Tenant.objects.filter(name=host_name).all().values('name'))
                    if len(hosts):
                        host_name = hosts[0]['name']
                        set_db_for_router(host_name, default_config)
                except:
                    message = get_error_message()
                    pass
        response = self.get_response(request)
        return response


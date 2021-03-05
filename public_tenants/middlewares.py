import threading
from psycopg2 import sql
from django.conf import settings
from django.db import connection

from dj_utils.methods import get_error_message

THREAD_LOCAL = threading.local()


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_db = connection.settings_dict['NAME']
        sub_domain = request.get_host().split(":")[0].lower()
        arr = sub_domain.split('.')
        if arr:
            if len(arr):
                host_name = arr[0]
                if not host_name:
                    return
                if current_db == host_name:
                    return
        if host_name and not host_name.startswith('localhost') and not host_name.startswith('127'):
            if current_db != host_name:
                default_config = settings.DATABASES['default']
                shared_db = default_config['NAME']
                if current_db != shared_db:
                    set_db_for_router(shared_db)
                try:
                    cur = connection.cursor()
                    query = "select name from public_tenants_tenant where name='{}'"
                    cur.execute(sql.SQL(query).format(sql.Identifier(host_name)))
                    hosts = cur.fetchall()
                    if len(hosts):
                        host_name = hosts[0]
                        if not settings.DATABASES.get(host_name):
                            tenant_config = default_config.copy()
                            tenant_config['NAME'] = host_name
                            settings.DATABASES[host_name] = tenant_config
                        set_db_for_router(host_name)
                except:
                    message = get_error_message()
                    pass
        response = self.get_response(request)
        return response


def get_current_db_name():
    res = getattr(THREAD_LOCAL, "DB", None)
    return res


def set_db_for_router(db):
    setattr(THREAD_LOCAL, "DB", db)

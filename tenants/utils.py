from django.db import connection
from tenants.models import Tenant


def hostname_from_request(request):
    # split on `:` to remove port
    return request.get_host().split(":")[0].lower()


def tenant_db_from_request(request):
    hostname = hostname_from_request(request)
    map = get_tenants_map()
    res = map[hostname]
    return res


def get_tenants_map():
    return {"thor.polls.local": "thor", "potter.polls.local": "potter"}

from django.db import connection
from public_tenants.models import Tenant


def hostname_from_request(request):
    # split on `:` to remove port
    return request.get_host().split(":")[0].lower()


def tenant_db_from_request(request):
    hostname = hostname_from_request(request)
    mapping = get_tenants_map()
    res = mapping[hostname]
    return res


def get_tenants_map():
    return {
        "thor.polls.local": "thor",
        "potter.polls.local": "potter",
        "localhost": "default",
        "127.0.0.1": "default"
    }

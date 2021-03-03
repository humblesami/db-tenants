from django.urls import path
from public_tenants.views import get_tenant_apps

urlpatterns = [
    path("get-apps/", get_tenant_apps),
]


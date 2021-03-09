from django.urls import path
from tenant_management.views import get_all_apps

urlpatterns = [
    path("get-apps/", get_all_apps),
]

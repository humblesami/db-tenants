from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"", include("polls.urls")),
    path("tenant/", include("tenant_management.urls")),
    path("subscription/", include("package_subscriptions.urls"))
]

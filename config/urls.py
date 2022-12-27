from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("chart.urls")),
    path("admin/", admin.site.urls),
]

handler404 = "chart.views.page_not_found"

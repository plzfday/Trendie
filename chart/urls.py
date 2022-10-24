from django.urls import path

from . import views

app_name = "chart"

urlpatterns = [
    path("", views.index, name="index"),
    path("tickers/", views.find_ticker, name="ticker"),
    path("keywords/", views.keywords, name="keywords"),
    path("company/<str:ticker>/", views.inquiry, name="inquiry"),
]

from django.urls import path

from . import views

app_name = "chart"

urlpatterns = [
    path("", views.index, name="index"),
    path("tickers/", views.find_ticker, name="ticker"),
    path("keywords/", views.keywords, name="keywords"),
    path("keywords/edit", views.keywords_edit, name="keywords_edit"),
    path("keywords/edit_complete", views.keywords_edit_complete, name="keywords_edit_complete"),
    path("company/<str:ticker>/", views.inquiry, name="inquiry"),
]

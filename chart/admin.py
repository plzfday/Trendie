from django.contrib import admin

from .models import Ticker


class TickerAdmin(admin.ModelAdmin):
    search_fields = ['ticker']


admin.site.register(Ticker, TickerAdmin)

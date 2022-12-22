from django.contrib import admin

from .models import Keyword


class KeywordAdmin(admin.ModelAdmin):
    search_fields = ['ticker']


admin.site.register(Keyword, KeywordAdmin)

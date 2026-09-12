from django.contrib import admin

from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "phone", "created_at")
    search_fields = ("name", "phone", "owner__username")
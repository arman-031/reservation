from django.contrib import admin

from .models import Business ,Staff


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "phone", "created_at")
    search_fields = ("name", "phone", "owner__username")
    
    
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "phone", "is_active")
    list_filter = ("is_active", "business")
    search_fields = ("name", "phone", "business__name")
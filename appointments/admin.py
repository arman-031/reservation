from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
	list_display = ("customer", "service", "date", "start_time", "status")
	list_filter = ("status", "date")
	search_fields = ("customer__username", "service__name")

from django.contrib import admin

from . import models
from django.contrib import admin


class ReservationInline(admin.TabularInline):
    model = models.Reservation


@admin.register(models.ReservationDay)
class ReservationDayAdmin(admin.ModelAdmin):
    list_display = ('date',)
    ordering = ('-date',)
    inlines = (ReservationInline,)

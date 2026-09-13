from django.conf import settings
from django.db import models


class Business(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="businesses",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
    
class Staff(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="staff",
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    services = models.ManyToManyField(
        "services.Service",
        related_name="staff_members",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
    
    
class WorkingHours(models.Model):
    class WeekDay(models.IntegerChoices):
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="working_hours",
    )
    day_of_week = models.PositiveSmallIntegerField(
        choices=WeekDay.choices,
    )
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "day_of_week"],
                name="unique_business_working_day",
            )
        ]

    def __str__(self):
        return f"{self.business.name} - {self.get_day_of_week_display()}"
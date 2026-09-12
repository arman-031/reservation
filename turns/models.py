from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ReservationDay(models.Model):
    date = models.DateField(_('Date'))

    class Meta:
        verbose_name = _('روز')
        verbose_name_plural=('روزها')
        ordering = ('-date',)

    def __str__(self):
        return str(self.date)

class Reservation(models.Model):
    dey=models.ForeignKey(ReservationDay,on_delete=models.CASCADE,verbose_name=_('روز'),related_name='reservations')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,verbose_name=_('user'))
    time = models.TimeField(_('Time'))

    class Meta:
        verbose_name = _('رزرو')
        verbose_name_plural = ('رزروها')
        ordering = ('time',)

    def __str__(self):
        return f"{self.user} - {self.dey} - {self.time}"

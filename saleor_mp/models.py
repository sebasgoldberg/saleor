from django.db import models
from django.conf import settings
from datetime import datetime

from saleor.order.models import Order

class Payment(models.Model):

    class STATUS:
        APPROVED = 'approved'
        REJECTED = 'rejected'
    
    class STATUS_DETAIL:
        ACCREDITED = 'accredited'
    
    class Meta:
        unique_together = [['mp_id', 'date_last_updated'], ]

    mp_id = models.CharField(
        max_length=60
    )

    date_last_updated = models.DateTimeField()

    order = models.ForeignKey(
        Order, related_name="mppayments", editable=False, on_delete=models.CASCADE
    )

    mp_status = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )

    mp_status_detail = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )

    currency_id = models.CharField(max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH, default='ARS')

    mp_transaction_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )

    total_paid_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )

    net_received_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )

    insertion_time = models.DateTimeField(auto_now_add=True)

    def is_approved(self):
        return self.mp_status == Payment.STATUS.APPROVED

    def is_captured(self):
        return ( self.is_approved() and 
            self.mp_status_detail == Payment.STATUS_DETAIL.ACCREDITED )

    def is_rejected(self):
        return self.mp_status == Payment.STATUS.REJECTED

    def get_error(self):
        if self.is_rejected():
            return self.mp_status_detail
        return None
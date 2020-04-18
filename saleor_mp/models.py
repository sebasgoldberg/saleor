from decimal import Decimal

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

    mp_id = models.CharField(
        max_length=60,
        unique=True
    )

    order = models.ForeignKey(
        Order, related_name="mppayments", editable=False, on_delete=models.CASCADE
    )

    date_last_updated = models.DateTimeField()

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

    update_time = models.DateTimeField(auto_now=True)

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
    
    @staticmethod
    def update_or_create(mp_id, defaults):

        payment, created = Payment.objects.update_or_create(
            mp_id=mp_id,
            defaults=defaults,
        )

        _defaults = defaults.copy()
        del _defaults['order']

        PaymentTrace.objects.update_or_create(
            mp_payment=payment,
            date_last_updated=defaults['date_last_updated'],
            defaults=_defaults,
        )

        return payment, created

    def register_refund(self, mp_refund_id, amount, date_created, status):

        return Refund.objects.update_or_create(
            mp_refund_id = mp_refund_id,
            defaults={
                'mp_payment': self,
                'amount': Decimal(amount),
                'date_created': date_created,
                'status': status,
            }
        )


class PaymentTrace(models.Model):

    class Meta:
        unique_together = [['mp_payment', 'date_last_updated'], ]

    mp_payment = models.ForeignKey(
        Payment, related_name="trace", editable=False, on_delete=models.CASCADE
    )

    date_last_updated = models.DateTimeField()

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

class Refund(models.Model):

    mp_refund_id = models.CharField(
        max_length=60,
        unique=True
    )

    mp_payment = models.ForeignKey(
        Payment, editable=False, on_delete=models.CASCADE
    )

    date_created = models.DateTimeField()

    amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )

    status = models.CharField(
        max_length=60,
        null=True,
        blank=True
    )
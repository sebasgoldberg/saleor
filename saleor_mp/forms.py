from django import forms
from django.utils.translation import pgettext_lazy, ugettext_lazy as _

from .models import Payment

class MercadopagoPaymentForm(forms.Form):

    preference_id = forms.CharField(
        label=pgettext_lazy("Preference ID", "Payment status")
    )

    def __init__(self, order, *args, **kwargs):
        super(MercadopagoPaymentForm, self).__init__(*args, **kwargs)
        self.order = order

    def is_valid(self):
        # Acá deberia validarse si ya fue realizado el pago
        # try:

        #     mppayment = self.order.mppayments.exists()

        #     if mppayment.status == Payment.STATUS.APPROVED and
        #         mppayment.status_detail == Payment.STATUS_DETAIL.ACCREDITED:
        #         return True

        # except Payment.DoesNotExist:
        #     pass

        # return False
        return self.order.mppayments.exists()
        

    def get_payment_token(self):
        """Return selected charge status instead of token for testing only.

        Gateways used for production should return an actual token instead.
        """
        # preference_id = self.cleaned_data["preference_id"]
        # return preference_id
        return self.order.mppayments.last().mp_id
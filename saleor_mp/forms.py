from django import forms
from django.utils.translation import pgettext_lazy, ugettext_lazy as _

class MercadopagoPaymentForm(forms.Form):

    preference_id = forms.CharField(
        label=pgettext_lazy("Preference ID", "Payment status")
    )

    def is_valid(self):
        # Acá deberia validarse si ya fue realizado el pago
        return False

    def get_payment_token(self):
        """Return selected charge status instead of token for testing only.

        Gateways used for production should return an actual token instead.
        """
        preference_id = self.cleaned_data["preference_id"]
        return preference_id
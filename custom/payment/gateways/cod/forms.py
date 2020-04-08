from django import forms
from django.utils.translation import pgettext_lazy, ugettext_lazy as _

class CODPaymentForm(forms.Form):

    # def get_payment_token(self):
    #     """Return selected charge status instead of token for testing only.

    #     Gateways used for production should return an actual token instead.
    #     """
    #     charge_status = self.cleaned_data["charge_status"]
    #     return charge_status

    def get_payment_token(self):
        """Return selected charge status instead of token for testing only.

        Gateways used for production should return an actual token instead.
        """
        # charge_status = self.cleaned_data["charge_status"]
        # return charge_status
        return "123"

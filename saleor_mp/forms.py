from django import forms
from django.utils.translation import pgettext_lazy, ugettext_lazy as _

class MercadopagoPaymentForm(forms.Form):

    preference_id = forms.CharField(
        label=pgettext_lazy("Preference ID", "Payment status")
    )

    def __init__(self, *args, **kwargs):
        super(MercadopagoPaymentForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        super(MercadopagoPaymentForm, self).is_valid()
        return False

    def get_payment_token(self):
        # This does not make sense, because the form never `is_valid`
        return self.cleaned_data['preference_id']
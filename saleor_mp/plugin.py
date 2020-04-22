import uuid

from typing import TYPE_CHECKING

from django.utils.translation import pgettext_lazy

from django.conf import settings

from saleor.extensions import ConfigurationTypeField
from saleor.extensions.base_plugin import BasePlugin

from saleor.payment import ChargeStatus, TransactionKind

from saleor.payment.interface import GatewayConfig, GatewayResponse, PaymentData

from .forms import MercadopagoPaymentForm

from saleor.order.models import Order

from . import create_preference, refund_payment

GATEWAY_NAME = "Mercadopago"

if TYPE_CHECKING:
    from ...interface import GatewayResponse, PaymentData, TokenConfig
    from django import forms

def require_active_plugin(fn):
    def wrapped(self, *args, **kwargs):
        previous = kwargs.get("previous_value", None)
        self._initialize_plugin_configuration()
        if not self.active:
            return previous
        return fn(self, *args, **kwargs)

    return wrapped


class MercadopagoGatewayPlugin(BasePlugin):
    PLUGIN_NAME = GATEWAY_NAME
    CONFIG_STRUCTURE = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = True
        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=True,
            connection_params={},
            template_path="templates/mercadopago.html",
            store_customer=False,
        )

    def _initialize_plugin_configuration(self):
        super()._initialize_plugin_configuration()

        if self._cached_config and self._cached_config.configuration:
            self.config = GatewayConfig(
                gateway_name=GATEWAY_NAME,
                auto_capture=True,
                connection_params={},
                template_path="",
                store_customer=False,
            )

    @classmethod
    def _get_default_configuration(cls):
        defaults = {
            "name": cls.PLUGIN_NAME,
            "description": "",
            "active": True,
            "configuration": [
                # {"name": "Store customers card", "value": False},
                # {"name": "Automatic payment capture", "value": True},
                # {"name": "Template path", "value": "order/payment/dummy.html"},
            ],
        }
        return defaults

    def _get_gateway_config(self):
        return self.config

    @require_active_plugin
    def authorize_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return previous_value

    @require_active_plugin
    def capture_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return previous_value

    @require_active_plugin
    def confirm_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return previous_value

    @require_active_plugin
    def refund_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return refund_payment(payment_information, previous_value)

    @require_active_plugin
    def void_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return previous_value

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        # There is no process payment, because the gateway sends
        # requests to modify the payment status.
        return previous_value

    @require_active_plugin
    def create_form(
        self, data, payment_information: "PaymentData", previous_value
    ) -> "forms.Form":

        preference = create_preference(payment_information)

        return MercadopagoPaymentForm(
            data={'preference_id': preference['id']}
            )

    @require_active_plugin
    def get_client_token(self, token_config: "TokenConfig", previous_value):
        return str(uuid.uuid4())

    @require_active_plugin
    def get_payment_template(self, previous_value) -> str:
        return "saleor_mp/mercadopago.html"

    @require_active_plugin
    def get_payment_config(self, previous_value):
        config = self._get_gateway_config()
        return [
            {"field": "store_customer_card", "value": config.store_customer},
            {"field": "client_token", "value": settings.SALEOR_MP_PUBLIC_KEY},
        ]

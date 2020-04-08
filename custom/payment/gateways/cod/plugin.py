import uuid

from typing import TYPE_CHECKING

from django.utils.translation import pgettext_lazy

from saleor.extensions import ConfigurationTypeField
from saleor.extensions.base_plugin import BasePlugin

from saleor.payment import ChargeStatus, TransactionKind

from saleor.payment.interface import GatewayConfig, GatewayResponse, PaymentData

from .forms import CODPaymentForm



GATEWAY_NAME = "Pago en entrega"

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


class CODGatewayPlugin(BasePlugin):
    PLUGIN_NAME = GATEWAY_NAME
    CONFIG_STRUCTURE = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = True
        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=True,
            connection_params={},
            template_path="",
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

    def _payment_action(
        self, payment_information: "PaymentData", transaction_kind: str
    ) -> "GatewayResponse":
        return GatewayResponse(
            is_success=True,
            action_required=False,
            kind=transaction_kind,
            amount=payment_information.amount,
            currency=payment_information.currency,
            transaction_id=payment_information.token,
            error=None,
        )

    @require_active_plugin
    def authorize_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return self._payment_action(payment_information, TransactionKind.AUTH)

    @require_active_plugin
    def capture_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return self._payment_action(payment_information, TransactionKind.CAPTURE)

    @require_active_plugin
    def confirm_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return self._payment_action(payment_information, TransactionKind.CAPTURE)

    @require_active_plugin
    def refund_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return self._payment_action(payment_information, TransactionKind.REFUND)

    @require_active_plugin
    def void_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return  self._payment_action(payment_information, TransactionKind.VOID)

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        """Process the payment."""
        return  self._payment_action(payment_information, TransactionKind.AUTH)

    @require_active_plugin
    def create_form(
        self, data, payment_information: "PaymentData", previous_value
    ) -> "forms.Form":
        return CODPaymentForm(data=data)

    @require_active_plugin
    def get_client_token(self, token_config: "TokenConfig", previous_value):
        return str(uuid.uuid4())

    @require_active_plugin
    def get_payment_template(self, previous_value) -> str:
        return "order/payment/dummy.html"

    @require_active_plugin
    def get_payment_config(self, previous_value):
        return [{"field": "store_customer_card", "value": False}]

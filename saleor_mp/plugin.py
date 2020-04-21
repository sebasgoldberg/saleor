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

from .models import Payment as PaymentMP

import mercadopago


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

    def _payment_action(
        self, payment_information: "PaymentData", transaction_kind: str
    ) -> "GatewayResponse":
        # return NotImplemented
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

        mp = mercadopago.MP(settings.SALEOR_MP_ACCESS_TOKEN)
        response = mp.post(
            "/v1/payments/{}/refunds".format(payment_information.token),
            { "amount": float(payment_information.amount) }
            )

        if response['status'] != 201:
            message = response['response']['message']
            return GatewayResponse(
                is_success=False,
                action_required=True,
                kind=TransactionKind.REFUND,
                amount=payment_information.amount,
                currency=payment_information.currency,
                transaction_id=payment_information.token,
                error=message,
            )

        p = PaymentMP.objects.filter(mp_id=payment_information.token).last()
        refund_data = response['response']

        refund, _ = p.register_refund(refund_data['id'], refund_data['amount'], refund_data['date_created'], refund_data['status'])

        return GatewayResponse(
                is_success=True,
                action_required=False,
                kind=TransactionKind.REFUND,
                amount=refund.amount,
                currency=p.currency_id,
                transaction_id=payment_information.token,
                error=None,
            )

    @require_active_plugin
    def void_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return  self._payment_action(payment_information, TransactionKind.VOID)

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return previous_value
        """Process the payment."""
        # order = Order.objects.get(pk=payment_information.order_id)
        # mppayment = order.mppayments.last()
        return GatewayResponse(
            # is_success=mppayment.is_approved(),
            # action_required=(not mppayment.is_approved()),
            # kind=( TransactionKind.CAPTURE if mppayment.is_approved() else TransactionKind.AUTH ),
            # amount=mppayment.total_paid_amount,
            # currency=mppayment.currency_id,
            # transaction_id=payment_information.token,
            # error=mppayment.get_error(),
            is_success=True,
            action_required=True,
            kind=TransactionKind.WAITING_FOR_AUTH,
            amount=0,
            currency=payment_information.currency,
            transaction_id=payment_information.token,
            error="",
        )


    def _create_preference(self, payment_information: "PaymentData"):

        mp = mercadopago.MP(settings.SALEOR_MP_ACCESS_TOKEN)

        options = {
            # # "auto_return": "approved",
            # "back_urls": {
            #     "failure": '{}/failure/{}'.format(
            #         settings.SALEOR_MP_BACK_URL_BASE,
            #         payment_information.order_id), 
            #     "pending": '{}/pending/{}'.format(
            #         settings.SALEOR_MP_BACK_URL_BASE,
            #         payment_information.order_id),
            #     "success": '{}/success/{}'.format(
            #         settings.SALEOR_MP_BACK_URL_BASE,
            #         payment_information.order_id),
            # },
            "items": [
                {
                    "title": "La Agroecológica - Pedido #{}".format(payment_information.order_id),
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": float(payment_information.amount)
                }
            ],
            'notification_url': '{}/{}/{}/'.format(
                settings.SALEOR_MP_NOTIFICATION_URL_BASE,
                payment_information.order_id,
                settings.SALEOR_MP_SECRET),
            # 'redirect_urls': { 
            #     'failure': 'https://agroeco.iamsoft.org/redirect_urls/failure/{}'.format(payment_information.order_id), 
            #     'pending': 'https://agroeco.iamsoft.org/redirect_urls/pending/{}'.format(payment_information.order_id),
            #     'success': 'https://agroeco.iamsoft.org/redirect_urls/success/{}'.format(payment_information.order_id),
            # },
        }

        # TODO Tratar errores.
        response = mp.create_preference(options)
        preference = response['response']
        return preference

    @require_active_plugin
    def create_form(
        self, data, payment_information: "PaymentData", previous_value
    ) -> "forms.Form":

        preference = self._create_preference(payment_information)

        return MercadopagoPaymentForm(
            Order.objects.get(pk=payment_information.order_id),
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

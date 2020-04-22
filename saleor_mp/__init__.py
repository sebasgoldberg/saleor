from django.conf import settings

from saleor.payment.interface import PaymentData, GatewayResponse
from saleor.payment import TransactionKind

import mercadopago

def create_preference(payment_information: PaymentData):

    mp = mercadopago.MP(settings.SALEOR_MP_ACCESS_TOKEN)

    # TODO Register the order as external ID of the preference.
    # TODO Add the information required to assure the payment would be processed sucessfully.
    options = {
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
    }

    # TODO Tratar errores.
    response = mp.create_preference(options)
    preference = response['response']
    return preference

def refund_payment(
    payment_information: PaymentData, previous_value
) -> GatewayResponse:

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

    refund_data = response['response']

    from decimal import Decimal

    return GatewayResponse(
            is_success=True,
            action_required=False,
            kind=TransactionKind.REFUND,
            amount=Decimal(refund_data['amount']),
            currency=payment_information.currency,
            transaction_id=refund_data['id'],
            error=None,
        )


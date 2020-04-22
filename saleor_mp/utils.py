from saleor.payment.utils import gateway_postprocess, create_transaction, create_payment_information
from saleor.payment.interface import GatewayResponse
from django.db import transaction

def process_mercadopago_transaction(order, kind, payment_id, amount, currency):

    with transaction.atomic():
        payment = order.payments.filter(gateway="Mercadopago").last()

        payment_data = create_payment_information(
            payment=payment, payment_token=payment_id
        )

        gateway_response = GatewayResponse(
            is_success=True,
            action_required=False,
            kind=kind,
            amount=amount,
            currency=currency,
            transaction_id=payment_id,
            error="",
        )

        trx = create_transaction(
            payment=payment,
            kind=kind,
            payment_information=payment_data,
            error_msg="",
            gateway_response=gateway_response,
        )

        gateway_postprocess(trx, trx.payment)

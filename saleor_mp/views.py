from decimal import Decimal
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

from saleor.order.models import Order
from saleor.order.actions import mark_order_as_paid

from saleor.payment import ChargeStatus, TransactionKind
from saleor.extensions.manager import get_extensions_manager

import mercadopago

from .utils import process_mercadopago_transaction

@csrf_exempt
def notification(request, order_id, secret):
    """
    request.GET:
        'id':'1276262186'
        'topic':'merchant_order'
    """

    # TODO Add support for duplicated notifications.

    # TODO Ver qué hacer con merchant_order y entender diferencia entre merchant_order y payment.

    # Validar que order_id y secret se corresponden.
    if settings.SALEOR_MP_SECRET != secret:
        return HttpResponse(status=501)

    if not ( "data.id" in request.GET and "type" in request.GET ):
        # TODO Creo que deveria retornar 201
        return HttpResponse(status=502)

    type = request.GET["type"] # payment

    # Obtener las informaciones del pago.
    payment_id = request.GET["data.id"]
    mp = mercadopago.MP(settings.SALEOR_MP_ACCESS_TOKEN)
    get_payment_response = mp.get_payment(payment_id)

    if get_payment_response["status"] != 200:
        return HttpResponse(status=503)

    mp_payment_info = get_payment_response['response']

    # Crear o actualizar las informaciones de pago para la orden y
    # marcar la orden como pagada caso corresponda (validar estatus y
    # monto del pago).
    order = Order.objects.get(pk=order_id)


    # TODO Verificar status
    WAITING_STATES = [ 'authorized', 'in_process', 'pending', ]
    APPROVED_STATES = [ 'approved', ]
    REJECTED_STATES = [ 'cancelled', 'rejected',]
    CANCELLED_STATES = [ 'charged_back', 'vacated', ]

    kind = None
    amount = Decimal(0)

    if mp_payment_info['status'] in WAITING_STATES:
        kind = TransactionKind.WAIT_FOR_AUTH
    elif mp_payment_info['status'] in APPROVED_STATES and mp_payment_info['status_detail'] == 'accredited':
        kind = TransactionKind.CAPTURE
        amount = Decimal(mp_payment_info['transaction_amount'])
    elif mp_payment_info['status'] in REJECTED_STATES:
        kind = TransactionKind.REJECT
    elif mp_payment_info['status'] in CANCELLED_STATES:
        kind = TransactionKind.CANCEL

    if kind is None:
        return HttpResponse(status=201)

    process_mercadopago_transaction(
        order,
        kind,
        payment_id,
        amount,
        mp_payment_info['currency_id']
        )

    return HttpResponse(status=201)


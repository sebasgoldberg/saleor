from decimal import Decimal
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from saleor.order.models import Order
from saleor.order.actions import mark_order_as_paid

from saleor.payment import ChargeStatus
from saleor.extensions.manager import get_extensions_manager

from .models import Payment as PaymentMP

import mercadopago

@csrf_exempt
def notification(request, order_id, secret):
    """
    request.GET:
        'id':'1276262186'
        'topic':'merchant_order'
    """

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

    date_last_updated = datetime.strptime(mp_payment_info['date_last_updated'].replace(':',''),'%Y-%m-%dT%H%M%S.%f%z')

    PaymentMP.update_or_create(payment_id, {
            'date_last_updated': date_last_updated,
            'order': order,
            'mp_status': mp_payment_info['status'],
            'mp_status_detail': mp_payment_info['status_detail'],
            'currency_id': mp_payment_info['currency_id'],
            'mp_transaction_amount': Decimal(mp_payment_info['transaction_amount']),
            'total_paid_amount': Decimal(mp_payment_info['transaction_details']['total_paid_amount']),
            'net_received_amount': Decimal(mp_payment_info['transaction_details']['net_received_amount']),
            })

    return HttpResponse(status=201)

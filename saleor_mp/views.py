from decimal import Decimal

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
    @todo: Registrar el resultado del pago
    request.GET:
        'id':'1276262186'
        'topic':'merchant_order'
    """

    # @todo Ver qué hacer con merchant_order y entender diferencia entre merchant_order y payment.

    # Validar que order_id y secret se corresponden.
    if settings.SALEOR_MP_SECRET != secret:
        return HttpResponse(status=500)

    if not ( "data.id" in request.GET and "type" in request.GET ):
        # @todo Creo que deveria retornar 201
        return HttpResponse(status=500)

    type = request.GET["type"] # payment

    # Obtener las informaciones del pago.
    payment_id = request.GET["data.id"]
    mp = mercadopago.MP(settings.SALEOR_MP_ACCESS_TOKEN)
    get_payment_response = mp.get_payment(payment_id)

    if get_payment_response["status"] != 200:
        return HttpResponse(status=500)

    mp_payment_info = get_payment_response['response']

    # Crear o actualizar las informaciones de pago para la orden y
    # marcar la orden como pagada caso corresponda (validar estatus y
    # monto del pago).
    order = Order.objects.get(pk=order_id)

    # payment = order.payments.filter(gateway='Mercadopago', charge_status=ChargeStatus.NOT_CHARGED).last()

    # if ( mp_payment_info['status'] == 'approved' and 
    #     mp_payment_info['status_detail'] == 'accredited' and 

    #     # @todo Validar si es correcto tomar total_gross_amount (podrían aplicar descuentos, etc.)
    #     mp_payment_info['transaction_amount'] >= float(payment.total) ):

    #     payment.charge_status = ChargeStatus.FULLY_CHARGED
    #     payment.captured_amount = payment.total
    #     payment.save(update_fields=["captured_amount", "charge_status"])

    #     manager = get_extensions_manager()
    #     manager.order_fully_paid(order)
    #     manager.order_updated(order)

    paymentMP, created = PaymentMP.objects.update_or_create(
        mp_id=payment_id, 
        defaults={
            'order': order,
            'mp_status': mp_payment_info['status'],
            'mp_status_detail': mp_payment_info['status_detail'],
            'mp_transaction_amount': Decimal(mp_payment_info['transaction_amount'])
            },
    )

    # @todo Tratar otros status: En caso de ser cancelado un pago, 
    # hacer las modificaciones que correspondan.

    return HttpResponse(status=201)

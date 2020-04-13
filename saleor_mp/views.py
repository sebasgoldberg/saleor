from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def notification(request, order_id, secret):
    """
    @todo: Registrar el resultado del pago
    request.GET:
        'id':'1276262186'
        'topic':'merchant_order'
    """
    # Validar que order_id y secret se corresponden.
    # Obtener las informaciones del pago.
    # Crear o actualizar las informaciones de pago para la orden.
    return HttpResponse(status=500)
    return HttpResponse(status=201)

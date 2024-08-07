from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from orders.models import Order


def process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        for item in order.items.all():
            session_data['line_items'].append(
                {
                    'price_data': {
                        'unit_amount': int(item.price * Decimal('100')),
                        'currency': 'usd',
                    },
                    'product_data': item.product.name,
                    'quantity': item.quantity,
                }
            )
            # TODO create session process for ourpaymentserver
            session = ...
            return redirect(session.url, code=303)
    else:
        return render(
            request,
            'payment/process.html',
            locals()
        )


def completed(request):
    return render(
        request,
        'payment/completed.html'
    )


def canceled(request):
    return render(
        request,
        'payment/canceled.html'
    )

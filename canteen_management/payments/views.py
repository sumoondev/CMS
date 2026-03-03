from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.utils import OperationalError, ProgrammingError
from types import SimpleNamespace
from orders.models import Order
from .models import Receipt


@login_required
def receipt_view(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)
    try:
        receipt = Receipt.objects.filter(order=order).first()
        if receipt is None:
            receipt = SimpleNamespace(id=f"TEMP-{order.id}")
    except (OperationalError, ProgrammingError):
        receipt = SimpleNamespace(id=f"TEMP-{order.id}")

    return render(request, "receipt.html", {
        "order": order,
        "receipt": receipt
    })
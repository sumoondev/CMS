import json
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404
from inventory.models import Inventory
from .models import Order, OrderItem
from  payments.models import  Payment, Receipt


@login_required
@require_POST
def checkout(request):

    data = json.loads(request.body)
    cart = data.get("cart", {})

    if not cart:
        return JsonResponse({"error": "Cart is empty"}, status=400)

    with transaction.atomic():
        # 1️⃣ Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=0
        )

        total_amount = Decimal("0.00")

        for item_id, item_data in cart.items():

            quantity = int(item_data["quantity"])

            inventory_item = get_object_or_404(Inventory, id=item_id)

            # 🔴 STOCK VALIDATION
            if inventory_item.quantity < quantity:
                return JsonResponse({
                    "error": f"Only {inventory_item.quantity} left for {inventory_item.item_name}"
                }, status=400)

            price = inventory_item.price

            # 2️⃣ Create OrderItem
            OrderItem.objects.create(
                order=order,
                item=inventory_item,
                quantity=quantity,
                price_at_purchase=price
            )

            # 3️⃣ Reduce stock
            inventory_item.quantity -= quantity

            # 4️⃣ Auto mark unavailable if zero
            if inventory_item.quantity == 0:
                inventory_item.is_available = False

            inventory_item.save()

            total_amount += price * quantity

        # 5️⃣ Update order
        order.total_amount = total_amount
        order.is_paid = True
        order.save()

    # 6️⃣ Create Payment
    # 7️⃣ Generate Receipt
    try:
        Payment.objects.create(
            order=order,
            payment_method="CASH",
            amount_paid=total_amount
        )
        Receipt.objects.create(order=order)
    except (OperationalError, ProgrammingError):
        pass

    return JsonResponse({
        "success": True,
        "order_id": order.id
    })

# Create your views here.

from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
import json
from .models import *
from orders.models import *
from django.contrib.auth.decorators import login_required


@login_required
def inventory_list(request):
    items = Inventory.objects.filter(is_available = True)
    context = {'inventory': items}
    return render(request, 'menu.html', context)


def add_to_cart(request):
    if request.method=="POST":
        data=json.loads(request.body)
        product_id=str(data.get("product_id"))
        product_id

        

    return render(request,'menu.html',context)

def payment_page(request):
    return HttpResponse("Payment Page")
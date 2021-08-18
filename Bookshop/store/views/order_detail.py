from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render

from store.models import Order


@login_required
def order_detail(request, order_id):
    try:
        chosen_order = Order.objects.get(pk=order_id)
    except ObjectDoesNotExist:
        messages.info(request, "Zamówienie nie istnieje bądź nie masz do niego dostępu")
        return HttpResponseRedirect('/')
    if request.user == chosen_order.user:
        context = {"order": chosen_order}
        return render(request, "order_detail.html", context)
    else:
        messages.info(request, "Zamówienie nie istnieje bądź nie masz do niego dostępu")
        return HttpResponseRedirect('/')

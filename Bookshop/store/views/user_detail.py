from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from store.models import Order, Complaint


@login_required
def user_detail(request):
    if isinstance(request.user, User):
        orders = Order.objects.filter(user=request.user)
        complaints = Complaint.objects.filter(user=request.user)
        context = {"orders": orders, "complaints": complaints, "user": request.user}
        return render(request, "user_detail.html", context)
    else:
        messages.info(request, "Wyłącznie dla zalogowanych użytkowników")
        return HttpResponseRedirect('/')

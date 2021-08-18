from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from store.forms import ComplaintForm
from store.models import Complaint
from store.models import Order
from store.models import OrderedProduct


@login_required
def complaint(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ComplaintForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                new_complaint = create_new_complaint(form, request)
                return HttpResponseRedirect('/complaint/' + str(new_complaint.id))
        else:
            form = ComplaintForm(user=request.user)
        context = {"form": form}
        return render(request, "complaint_form.html", context)
    else:
        messages.info(request, "Najpierw musisz się zalogować")
        return HttpResponseRedirect('/accounts/login/')


def create_new_complaint(form, request):
    print(form.cleaned_data['ordered_product'])
    new_complaint = Complaint(
        name=form.cleaned_data['name'],
        surname=form.cleaned_data['surname'],
        ordered_product=get_user_ordered_products(request.user)[int(form.cleaned_data['ordered_product']) - 1],
        message=form.cleaned_data['message'],
        user=request.user,
        product_photo=request.FILES.get('product_photo'),
        written_complaint=form.cleaned_data['additional_files']
    )
    new_complaint.save()
    return new_complaint


def get_user_ordered_products(user):
    ordered_products_list = []
    for order in Order.objects.filter(user=user):
        for product in OrderedProduct.objects.filter(order=order):
            ordered_products_list.append(product)
    return ordered_products_list

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from store.forms import OrderForm, DiscountForm
from store.models import Order, Delivery, OrderedProduct, Discount
from store.views.cart import get_products_in_cart, get_total_value_of_cart


@login_required
def order(request):
    if request.user.is_authenticated:
        products_to_order = get_products_in_cart(request)
        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                new_order = create_new_order(request, form)
                new_order.save()
                take_products_from_cart(request, new_order)
                if new_order.confirm_order():
                    return HttpResponseRedirect('/payment_method/' + str(new_order.id))
                else:
                    messages.info(request,
                                  "Niestety, produktu nie ma już na magazynie. Zamówienie nie zostało potwierdzone.")
        else:
            form = OrderForm()
        context = {"form": form, "products": products_to_order, "total": get_total_value_of_cart(request),
                   "number_of_products": len(products_to_order), "form_discount": DiscountForm()}
        return render(request, "order_form.html", context)
    else:
        messages.info(request, "Najpierw musisz się zalogować")
        return HttpResponseRedirect('/accounts/login/')


def create_new_order(request, form):
    new_order = Order(
        name=form.cleaned_data['name'],
        surname=form.cleaned_data['surname'],
        address=form.cleaned_data['street'] + " " + form.cleaned_data['apartment_number'] + "," +
                form.cleaned_data['shipping_country'] + " " + form.cleaned_data['shipping_zip'] + " " +
                form.cleaned_data['city'],
        delivery=Delivery.objects.filter(id=form.cleaned_data['delivery']).first(),
        phone_number=form.cleaned_data['phone_number']
    )
    if isinstance(request.user, User):
        new_order.user = request.user
    if 'discount_code' in request.session:
        new_order.discount = Discount.objects.get(code=request.session['discount_code'])
    return new_order


def take_products_from_cart(request, new_order):
    products_to_order = get_products_in_cart(request)
    for product, amount in products_to_order.items():
        OrderedProduct(product=product, order=new_order, amount=amount).save()


def add_discount_code(request):
    if request.method == "POST":
        form = DiscountForm(request.POST)
        if form.is_valid():
            if 'discount_code' not in request.session:
                if Discount.objects.filter(code=form.cleaned_data['discount_code']).exists():
                    request.session['discount_code'] = form.cleaned_data['discount_code']
                    messages.info(request, "Dodano kod")
                    request.session.modified = True
                else:
                    messages.info(request, "Niepoprawny kod")
            else:
                messages.info(request, "Można wykorzystać tylko jeden kod.")
    return HttpResponseRedirect('/order')

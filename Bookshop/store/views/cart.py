from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from store.models import Product, Discount


def add_to_cart(request):
    if request.method == "POST":
        product = Product.objects.get(id=request.POST.get('item_id', False))
        if 'cart' not in request.session:
            request.session['cart'] = {}
        if request.POST['item_id'] not in request.session['cart']:
            request.session['cart'][request.POST.get('item_id', False)] = 1
            messages.info(request, "Produkt został dodany do koszyka")
        else:
            if product.can_order_amount(request.session['cart'][request.POST.get('item_id', False)] + 1):
                request.session['cart'][request.POST.get('item_id', False)] += 1
                messages.info(request, "Ilość produktu została zaktualizowana")
            else:
                messages.info(request, "Brak większej ilości produktu w magazynie")
        request.session.modified = True
    return HttpResponseRedirect('/cart')


def remove_one_quantity_from_cart(request):
    if request.method == "POST":
        request.session['cart'][request.POST.get('item_id', False)] -= 1
        if request.session['cart'][request.POST.get('item_id', False)] == 0:
            del_from_cart(request)
        messages.info(request, "Ilość produktu została zaktualizowana")
        request.session.modified = True
    return HttpResponseRedirect('/cart')


def get_products_in_cart(request):
    products_in_cart = {}
    for item_id, amount in request.session.get('cart', {}).items():
        product = Product.objects.get(pk=item_id)
        products_in_cart[product] = amount
    return products_in_cart


def get_total_value_of_cart(request):
    total = 0
    for item_id, amount in request.session.get('cart', {}).items():
        product = Product.objects.get(pk=item_id)
        total += product.get_current_price() * amount
    if 'discount_code' in request.session:
        total = total * (1 - Discount.objects.get(code=request.session['discount_code']).percent)
    return round(total, 2)


def cart(request):
    total = 0
    products_in_cart = get_products_in_cart(request)
    for product, amount in products_in_cart.items():
        total += product.get_current_price() * amount
    context = {"products": products_in_cart,
               "cart_value": total}
    return render(request, "cart.html", context)


def del_from_cart(request):
    del request.session['cart'][request.POST.get('item_id')]
    request.session.modified = True
    messages.info(request, "Produkt został usunięty z koszyka")
    return HttpResponseRedirect('/cart')


def clean_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    return HttpResponseRedirect('/cart')

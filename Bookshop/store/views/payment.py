import stripe
from Bookshop import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from store.forms import PaymentMethodForm, PaymentForm
from store.models import Order, Payment, PaymentMethod



@login_required
def payment_method(request, order_id):
    try:
        chosen_order = Order.objects.get(pk=order_id)
    except ObjectDoesNotExist:
        messages.info(request, "Order does not exist")
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, delivery=chosen_order.delivery)
        if form.is_valid():
            request.session['cart'] = {}
            chosen_order.set_payment_type(form.cleaned_data['payment'])
            request.session['try'] = 0
            return HttpResponseRedirect('/payment/' + form.cleaned_data['payment'] + "/" + str(chosen_order.id))
    else:
        form = PaymentMethodForm(delivery=chosen_order.delivery)
    context = {"form": form, "order": chosen_order}
    return render(request, "payment_method.html", context)


@login_required
def payment(request, payment_method_id, order_id):
    chosen_order = Order.objects.get(id=order_id)
    form_inactive = PaymentMethodForm(request.POST, delivery=chosen_order.delivery)
    if payment_method_id == 1 and request.method == 'POST':
        if request.session['try'] < 2:
            request.session['try'] += 1
            form = PaymentForm(request.POST)
            if form.is_valid():
                token = form.cleaned_data.get('stripeToken')
                try:
                    print(request.session['try'])
                    charge = stripe.Charge.create(amount=int(chosen_order.get_total_price() * 100), currency='pln',
                                                  source=token)
                    new_payment = Payment(stripe_charge_id=charge['id'], user=request.user,
                                          amount=chosen_order.get_total_price(),
                                          type=PaymentMethod.objects.get(id=payment_method_id))
                    new_payment.save()
                    chosen_order.set_payment(new_payment)
                    return HttpResponseRedirect('/order/' + str(chosen_order.id))
                except stripe.error.CardError as e:
                    messages.info(request, "Płatność niepoprawna - nieprawidłowa karta")
                except stripe.error.RateLimitError as e:
                    messages.info(request, "Płatność niepoprawna - osiągnięto limit")
                except stripe.error.AuthenticationError as e:
                    messages.info(request, "Płatność niepoprawna- błąd identyfikacji")
                except stripe.error.APIConnectionError as e:
                    messages.info(request, "Płatność niepoprawna- problem z połaczeniem z serwerem")
                except Exception as e:
                    messages.info(request, "Płatność niepoprawna")
        else:
            chosen_order.unconfirm_order()
            request.session['try'] = 0
            messages.info(request, "Liczba prób przekroczyła 3. Zamówienie anulowane.")
            return HttpResponseRedirect('/../../')
    if payment_method_id == 2 or payment_method_id == 3:
        return HttpResponseRedirect('/order/' + str(chosen_order.id))
    else:
        context = {"form": form_inactive, "order": chosen_order, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY}
        return render(request, "payment_method.html", context)

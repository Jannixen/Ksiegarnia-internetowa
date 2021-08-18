from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from store.forms import OpinionForm
from store.models import Product, Opinion


def products_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = OpinionForm(request.POST)
        if form.is_valid():
            create_opinion(request, form, product)
            return HttpResponseRedirect('')
    else:
        form = OpinionForm()
    context = {"product": product, "form": form}
    return render(request, "product_detail.html", context)


def create_opinion(request, form, product):
    opinion = Opinion(
        product=product,
        comment=form.cleaned_data['comment'],
        rating=form.cleaned_data['rating']
    )
    if isinstance(request.user, User):
        opinion.user = request.user
    opinion.save()

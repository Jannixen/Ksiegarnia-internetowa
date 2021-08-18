from django.core.paginator import Paginator
from django.shortcuts import render

from store.models import Product

ITEMS_PER_PAGE = 9
GENRES_CATEGORIES = {
    "science": "Nauka",
    "fantasy": "Fantastyka",
    "religion": "Religie i wyznania",
    "biography": "Biografia",
    "sports": "Sport",
    "thriller": "Thriller",
    "crime": "Kryminał",
    "romance": "Romans",
    "historical": "Historia",
    "philosophy": "Filozofia",
    "horror": "Horror",
    "journalism": "Reportaż"}
GENRES_CATEGORIES = {k: v for k, v in sorted(GENRES_CATEGORIES.items(), key=lambda item: item[1])}


def products_list(request):
    products = Product.objects.all().order_by('id')
    paginator = Paginator(products, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_numbers = [i for i in range(1, page_obj.paginator.num_pages + 1)]
    context = {'products': page_obj, 'page_numbers': page_numbers,
               "genres_list": GENRES_CATEGORIES}
    return render(request, "products_list.html", context)


def products_list_searched(request):
    all_products = Product.objects.all().order_by('id')
    products = []
    if request.method == 'POST':
        searched = request.POST.get('searched')
        for product in all_products:
            if searched in product.title or searched.capitalize() in product.title or searched \
                    in product.author or searched.capitalize() in product.author:
                products.append(product)
    paginator = Paginator(products, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_numbers = [i for i in range(1, page_obj.paginator.num_pages + 1)]
    context = {'products': page_obj, 'page_numbers': page_numbers,
               "genres_list": GENRES_CATEGORIES}
    return render(request, "products_list.html", context)

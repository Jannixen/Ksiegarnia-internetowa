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


def genre_list(request, genre_name):
    products_for_genre_list = get_products_for_genre(genre_name)
    paginator = Paginator(products_for_genre_list, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_numbers = [i for i in range(page_obj.paginator.num_pages + 1)]
    context = {'products': page_obj, 'page_numbers': page_numbers,
               "genres_list": GENRES_CATEGORIES}
    return render(request, 'products_list.html', context)


def get_products_for_genre(genre_name):
    genre_name = genre_name.capitalize()
    all_products_list = Product.objects.all()
    products_for_genre_list = []
    for product in all_products_list:
        if genre_name in product.genre:
            products_for_genre_list.append(product)
    return products_for_genre_list

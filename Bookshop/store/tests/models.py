import random

import pandas as pd
from django.test import TestCase

from ..models import Opinion
from ..models import Order
from ..models import OrderedProduct
from ..models import Product


class ProductLoadTestCase(TestCase):

    def test_load_products(self):
        self.load_data(10)
        amy_tan_book = Product.objects.get(id=1)
        john_grisham_book = Product.objects.get(id=2)
        self.assertEqual(amy_tan_book.year, '1991')
        self.assertEqual(john_grisham_book.year, '1999')

    def get_data(self, n):
        data = pd.read_excel(open('store/sources/books_data.xlsx', 'rb'), sheet_name='Arkusz3')
        products_data = []
        for i in range(0, n):
            one_product_data = {data.iloc[i].index[0]: data.iloc[i].values[0],
                                data.iloc[i].index[1]: data.iloc[i].values[1],
                                data.iloc[i].index[2]: data.iloc[i].values[2],
                                data.iloc[i].index[3]: data.iloc[i].values[3],
                                data.iloc[i].index[4]: data.iloc[i].values[4],
                                data.iloc[i].index[6]: data.iloc[i].values[6],
                                data.iloc[i].index[8]: data.iloc[i].values[8],
                                data.iloc[i].index[9]: data.iloc[i].values[9]}
            products_data.append(one_product_data)
        return products_data

    def load_data(self, n):
        products = self.get_data(n)
        for i in range(0, n - 1):
            Product.objects.create(title=products[i]['Book-Title'],
                                   author=products[i]['Book-Author'],
                                   description=products[i]['Description'],
                                   genre=products[i]['Genre'],
                                   isbn=products[i]['ISBN'],
                                   price=random.randint(30, 45) - 0.01,
                                   publisher=products[i]['Publisher'],
                                   year=products[i]['Year-Of-Publication'],
                                   image_url=products[i]['Image-URL-M'],
                                   inventory=random.randint(1, 30))


class RatingCountTestCase(TestCase):
    def setUp(self):
        Product.objects.create(title="Ksiazka1")
        Opinion.objects.create(product=Product.objects.get(title="Ksiazka1"), comment="jakiś komentarz", rating=2)
        Opinion.objects.create(product=Product.objects.get(title="Ksiazka1"), comment="jakiś komentarz", rating=9)

    def test_product_rating_count(self):
        p1 = Product.objects.get(title="Ksiazka1")
        self.assertEqual(p1.get_total_rating(), 5.5)


class OpinionRatingBadValueTestCase(TestCase):
    def setUp(self):
        Product.objects.create(title="Ksiazka1")
        Opinion.objects.create(product=Product.objects.get(title="Ksiazka1"), comment="jakiś komentarz", rating=11)

    def test_rating_bad_value(self):
        assert False


class OrderTotalCostCountTestCase(TestCase):
    def setUp(self):
        p1 = Product.objects.create(title="Ksiazka1", price=33)
        p2 = Product.objects.create(title="Ksiazka2", price=35)
        p3 = Product.objects.create(title="Ksiazka3", price=41)
        order = Order.objects.create()
        ordered_p1 = OrderedProduct.objects.create(product=p1, order=order, amount=1)
        ordered_p2 = OrderedProduct.objects.create(product=p2, order=order, amount=1)
        ordered_p3 = OrderedProduct.objects.create(product=p3, order=order, amount=2)

    def test_total_order_cost_count(self):
        self.assertEqual(Order.objects.get(pk=1).get_total_price(), 150.0)

from django.forms import ModelForm, Form, IntegerField, Textarea, NumberInput, CharField, ChoiceField, \
    RadioSelect, TextInput, ImageField, FileField
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import Opinion, Delivery, Order, OrderedProduct


class OpinionForm(ModelForm):
    class Meta:
        model = Opinion
        fields = ['comment', 'rating']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 6}),
            'rating': NumberInput(attrs={'min': 1, 'max': 10, 'type': 'number'})
        }


def make_ordered_products_choice_tuple(user):
    ordered_products_list = []
    for order in Order.objects.filter(user=user):
        if order.ordered:
            for product in OrderedProduct.objects.filter(order=order):
                ordered_products_list.append(str(product) + ", zamówienie:" + str(order.id))
    return tuple(enumerate(ordered_products_list, 1))


class ComplaintForm(Form):
    name = CharField(required=True, label="Imię")
    surname = CharField(required=True, label="Nazwisko")
    ordered_product = ChoiceField()
    message = CharField(required=True, label="Powód reklamacji", widget=Textarea(attrs={
        'cols': 40,
        'rows': 6,
        'class': 'form-control',
        'placeholder': 'Proszę podać powód reklamacji',
    }))
    product_photo = ImageField(required=False, label="Zdjęcie produktu(opcjonalne)")
    additional_files = FileField(required=False, label="Dodatkowe pliki")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.ordered_products = make_ordered_products_choice_tuple(user)
        self.fields['ordered_product'] = ChoiceField(
            choices=self.ordered_products,
            label="Wybierz produkt do reklamacji")


class AmountForm(Form):
    amount = IntegerField(required=True, max_value=5, min_value=1, label='', initial=1,
                          widget=NumberInput(attrs={'size': '2'}))


class OrderForm(Form):
    name = CharField(required=True, label="Imię", max_length=100)
    surname = CharField(required=True, label="Nazwisko", max_length=100)
    street = CharField(required=True, label="Ulica i numer domu", max_length=40)
    apartment_number = CharField(required=False, label="Numer mieszkania", max_length=10)
    phone_number = CharField(required=True, label="Numer telefonu", min_length=9, max_length=9)
    city = CharField(required=True, label="Miasto", max_length=25)
    shipping_country = CountryField(blank_label='Polska', default="Polska", blank=True).formfield(label="Kraj dostawy",
                                                                                                  widget=CountrySelectWidget(
                                                                                                      attrs={
                                                                                                          'class': 'custom-select d-block w-100',
                                                                                                      }))
    shipping_zip = CharField(required=True, label="Kod pocztowy", min_length=5, max_length=5)
    delivery = ChoiceField(widget=RadioSelect, choices=tuple(enumerate(Delivery.objects.order_by('id'), 1)),
                           label="Dostawa")


class PaymentMethodForm(Form):
    available_payment_methods = []
    payment = ChoiceField()

    def __init__(self, *args, **kwargs):
        delivery = kwargs.pop('delivery')
        super().__init__(*args, **kwargs)
        self.available_payment_methods = delivery.payment_options.all()
        self.fields['payment'] = ChoiceField(widget=RadioSelect,
                                             choices=tuple(enumerate(self.available_payment_methods, 1)),
                                             label="Metoda płatności", required=False)


class DiscountForm(Form):
    discount_code = CharField(required=False, label="Kod rabatowy", widget=TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Kod rabatowy',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class PaymentForm(Form):
    stripeToken = CharField(required=False)

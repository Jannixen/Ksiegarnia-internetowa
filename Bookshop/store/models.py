from PIL import Image
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Product(models.Model):
    LABEL_CHOICES = (('BESTSELLER', 'primary'), ('NEW', 'secondary'), ('SALE', 'danger'))

    isbn = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    year = models.CharField(max_length=4)
    publisher = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    discount_price = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=1000, default='Opis jeszcze nie został dodany.')
    genre = models.CharField(max_length=200, default='')
    image_url = models.CharField(max_length=500)
    inventory = models.IntegerField(default=0)
    image_big_url = models.CharField(max_length=500)
    label = models.CharField(choices=LABEL_CHOICES, max_length=10, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rating = 0.0
        self._ratings_count = 0
        self._opinions = []

    def __str__(self):
        return self.title + "-" + self.isbn

    def can_order(self):
        if self.inventory > 0:
            return True
        return False

    def can_order_amount(self, amount):
        if self.inventory >= amount:
            return True
        return False

    def remove_from_inventory(self, amount):
        self.inventory -= amount
        self.save(update_fields=['inventory'])

    def add_to_inventory(self, amount):
        self.inventory += amount
        self.save(update_fields=['inventory'])

    def get_total_rating(self):
        opinions = self.opinion_set.all()
        avg_rate = 0
        if len(opinions) > 0:
            for opinion in opinions:
                avg_rate += opinion.rating
            avg_rate = avg_rate / len(opinions)
            return avg_rate
        else:
            return "Brak ocen"

    def get_opinions_list(self):
        self._opinions = self.opinion_set.all()
        if len(self._opinions) == 0:
            return ""
        else:
            return self._opinions

    def get_current_price(self):
        if self.discount_price is None:
            return self.price
        else:
            return self.discount_price


class Opinion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500)
    rating = models.IntegerField(
        default=10,
        validators=[MaxValueValidator(10), MinValueValidator(1)]
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


class Discount(models.Model):
    code = models.CharField(max_length=100)
    percent = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return self.code + " " + str(self.percent * 100)


class PaymentMethod(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type


class Delivery(models.Model):
    type = models.CharField(max_length=100)
    cost = models.FloatField(default=9.99)
    payment_options = models.ManyToManyField(PaymentMethod)

    def __str__(self):
        return self.type + " (cena: " + str(self.cost) + " zł)"


class Payment(models.Model):
    type = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    payment_date = models.DateTimeField(default=timezone.now)
    stripe_charge_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.payment_date) + "_" + "userid:" + str(self.user_id)


class Order(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=9)
    delivery = models.ForeignKey(Delivery, on_delete=models.PROTECT)
    discount_code = models.CharField(max_length=100, null=True, blank=True)
    ordered_products = models.ManyToManyField("Product", through='OrderedProduct')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    payment_type = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name + self.surname

    def get_total_price(self):
        total = 0
        ordered_products = OrderedProduct.objects.filter(order=self)
        for ordered_product in ordered_products:
            if self.discount:
                total += ordered_product.amount * ordered_product.product.get_current_price() * (
                        1 - self.discount.percent)
            else:
                total += ordered_product.amount * ordered_product.product.get_current_price()
        if self.delivery:
            total += self.delivery.cost
        return round(total, 2)

    def get_products(self):
        products = {}
        ordered_products = OrderedProduct.objects.filter(order=self)
        for ordered_product in ordered_products:
            products[ordered_product.product] = ordered_product.amount
        return products

    def get_number_of_products(self):
        number_of_products = 0
        ordered_products = OrderedProduct.objects.filter(order=self)
        for ordered_product in ordered_products:
            number_of_products += ordered_product.amount
        return number_of_products

    def confirm_order(self):
        if self.block_products():
            self.ordered = True
            self.save(update_fields=['ordered'])
            return True
        return False

    def block_products(self):
        for product, amount in self.get_products().items():
            if product.can_order():
                product.remove_from_inventory(amount)
            else:
                return False
        return True

    def unconfirm_order(self):
        if self.unblock_products():
            self.ordered = False
            self.save(update_fields=['ordered'])
            return True
        return False

    def unblock_products(self):
        for product, amount in self.get_products().items():
            if product.can_order():
                product.add_to_inventory(amount)
            else:
                return False
        return True

    def set_payment_type(self, payment_id):
        self.ordered = True
        self.payment_type = PaymentMethod.objects.get(id=payment_id)
        self.save(update_fields=['payment_type'])

    def get_payment_type(self):
        if self.payment_type:
            return str(self.payment_type)
        else:
            return ""

    def is_paid(self):
        if self.payment_type:
            return True
        return False

    def set_payment(self, payment):
        self.payment = payment
        self.save(update_fields=['payment'])


class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)

    def __str__(self):
        return self.product.__str__()

    def get_amount_price(self):
        return self.product.get_current_price() * self.amount


class Complaint(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    ordered_product = models.ForeignKey(OrderedProduct, on_delete=models.PROTECT)
    message = models.CharField(max_length=1000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    product_photo = models.ImageField(upload_to='uploads/', null=True, blank=True)
    written_complaint = models.FileField(upload_to='uploads/', null=True, blank=True)

    def __str__(self):
        return self.name + self.surname

    def save(self):
        super().save()
        img = Image.open(self.product_photo.path)
        if img.height > 300 or img.width > 300:
            new_img = (300, 300)
            img.thumbnail(new_img)
            img.save(self.product_photo.path)

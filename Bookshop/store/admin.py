from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(Complaint)
admin.site.register(Discount)
admin.site.register(Opinion)
admin.site.register(Order)
admin.site.register(OrderedProduct)
admin.site.register(PaymentMethod)
admin.site.register(Delivery)
admin.site.register(Payment)

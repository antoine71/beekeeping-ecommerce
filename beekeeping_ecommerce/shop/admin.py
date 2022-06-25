from django.contrib import admin
from pyparsing import Or

from .models import Product, Order, OrderProduct, BillingAddress, Payment, Invoice


admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(Invoice)

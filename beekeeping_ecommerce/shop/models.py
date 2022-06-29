from django.db import models

from django_countries.fields import CountryField
from autoslug import AutoSlugField
from requests import request


PAYMENT_CHOICES = (
    ("S", "Carte Bancaire"),
#    ("P", "Paypal"),
)

DELIVERY_CHOICES = (
    ("H", "Livraison à Domicile"),
#    ("P", "Livraison en Point Relais"),
)

ADDRESS_CHOICES = (
    ("B", "Facturation"),
    ("S", "Expédition"),
)


class Product(models.Model):
    name = models.CharField("Product name", max_length=100)
    price = models.FloatField("Product price EX VAT")
    slug = AutoSlugField(unique=True, always_update=True, populate_from="name")
    short_description = models.CharField("Product short description", max_length=100)
    long_description = models.TextField("Product description")
    is_availabile = models.BooleanField("Product is available")
    photo = models.ImageField(upload_to="product_photos")

    def __str__(self):
        return self.name

    def get_vat_price(self):
        return round(self.price / 0.8 - self.price, 2)

    def get_price_incl_vat(self):
        return self.price + self.get_vat_price()


class OrderProduct(models.Model):
    user_id = models.CharField("User id (session_key)", max_length=40)
    ordered = models.BooleanField("Order completed", default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField("Quantity", default="1")

    def get_order_product_price(self):
        return self.product.get_price_incl_vat() * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"


class ContactInfo(models.Model):
    email = models.EmailField("Adresse Email", null=True, blank=True)
    phone = models.CharField(
        "Numéro de téléphone", max_length=20, null=True, blank=True
    )

    def __str__(self):
        return f"{self.email}"


class Address(models.Model):
    first_name = models.CharField("Prénom", max_length=100)
    last_name = models.CharField("Nom", max_length=100)
    company_name = models.CharField(
        "Société", max_length=100, null=True, blank=True, help_text="Optionnel"
    )
    street_address = models.CharField("Adresse", max_length=100)
    street_address_line_2 = models.CharField(
        "Complément d'adresse",
        max_length=100,
        null=True,
        blank=True,
        help_text="Optionnel",
    )
    city = models.CharField("Ville", max_length=100)
    country = CountryField("Pays", multiple=False)
    zip_code = models.CharField("Code postal", max_length=15)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.address_type})"

    class Meta:
        verbose_name_plural = "Addresses"


class Payment(models.Model):
    stripe_intent_id = models.CharField(max_length=100)
    stripe_client_secret = models.CharField(max_length=100)
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=40, null=True, blank=True, default="created")

    def __str__(self):
        return f"{self.amount}, {self.status}"


class Order(models.Model):
    ref_code = models.CharField(max_length=20, default="0")
    user_id = models.CharField("User id (session_key)", max_length=40)
    products = models.ManyToManyField(OrderProduct, related_name="orders", blank=True)
    start_date = models.DateTimeField("Date created", auto_now_add=True)
    ordered_date = models.DateTimeField("Date ordered", null=True, blank=True)
    ordered = models.BooleanField("Order completed", default=False)
    contact_info = models.ForeignKey(
        ContactInfo,
        verbose_name="Client",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    shipping_address = models.ForeignKey(
        Address,
        verbose_name="Adresse de Livraison",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="shipping_address",
    )
    same_billing_address = models.BooleanField(default=True)
    billing_address = models.ForeignKey(
        Address,
        verbose_name="Adresse de facturation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="billing_address",
    )
    payment_option = models.CharField(
        "Options de payment", max_length=1, choices=PAYMENT_CHOICES
    )
    delivery_option = models.CharField(
        "Options de livraison", max_length=1, choices=DELIVERY_CHOICES
    )
    payment = models.OneToOneField(
        Payment, on_delete=models.SET_NULL, blank=True, null=True, related_name="order"
    )
    invoice = models.OneToOneField(
        "Invoice",
        verbose_name="Invoice",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    being_delivered = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def get_products_quantity(self):
        return sum(product.quantity for product in self.products.all())

    def get_order_price_ex_delivery(self):
        return sum(
            order_product.get_order_product_price()
            for order_product in self.products.all()
        )

    def get_order_delivery_price(self):
        return 5

    def get_order_total_price(self):
        return self.get_order_price_ex_delivery() + self.get_order_delivery_price()

    def delivery_verbose(self):
        return dict(DELIVERY_CHOICES)[self.delivery_option]

    def __str__(self):
        return self.ref_code


def get_invoice_number():
    invoice_qs = Invoice.objects.order_by("-id")
    if not invoice_qs.exists():
        invoice_id = 1
    else:
        invoice_id = invoice_qs[0].id + 1
    return f"NBS_ZEP_WEB_{str(invoice_id).zfill(5)}"


class Invoice(models.Model):

    invoice_number = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        self.invoice_number = get_invoice_number()
        super().save(*args, **kwargs)


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    message = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __srt__(self):
        return f"{self.pk}"

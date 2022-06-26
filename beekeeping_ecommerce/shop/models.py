from django.db import models
from django.forms import CharField

from django_countries.fields import CountryField
from autoslug import AutoSlugField


PAYMENT_CHOICES = (
    ("S", "Stripe"),
    ("P", "Paypal"),
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


class BillingAddress(models.Model):
    user_id = models.CharField("User id (session_key)", max_length=40)
    first_name = models.CharField("Prénom", max_length=100)
    last_name = models.CharField("Nom", max_length=100)
    company_name = models.CharField(
        "Société (optionnel)", max_length=100, null=True, blank=True, help_text="Optionnel"
    )
    street_address = models.CharField("Adresse", max_length=100)
    street_address_line_2 = models.CharField(
        "Complément d'adresse", max_length=100, null=True, blank=True, help_text="Optionnel"
    )
    city = models.CharField("Ville", max_length=100)
    country = CountryField("Pays", multiple=False)
    zip_code = models.CharField("Code postal", max_length=15)
    same_shipping_address = models.BooleanField(
        "L'adresse d'expédition est identique à l'adresse de facturation", default=True
    )
    payment_option = models.CharField(
        "Options de payment", max_length=1, choices=PAYMENT_CHOICES
    )
    email = models.CharField("Adresse Email", max_length=50)
    phone = models.CharField("Numéro de téléphone", max_length=50)

    def __str__(self):
        return f"{self.first_name}, {self.last_name}, {self.city}"


class Payment(models.Model):
    stripe_intent_id = models.CharField(max_length=100)
    stripe_client_secret = models.CharField(max_length=100)
    user_id = models.CharField("User id (session_key)", max_length=40)
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=40, null=True, blank=True, default="created")

    def __str__(self):
        return "qq"


class Order(models.Model):
    user_id = models.CharField("User id (session_key)", max_length=40)
    products = models.ManyToManyField(OrderProduct, related_name="orders", blank=True)
    start_date = models.DateTimeField("Date created", auto_now_add=True)
    ordered_date = models.DateTimeField("Date ordered", null=True, blank=True)
    ordered = models.BooleanField("Order completed", default=False)
    billing_address = models.OneToOneField(
        BillingAddress,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="order",
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

    def __str__(self):
        return self.user_id


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

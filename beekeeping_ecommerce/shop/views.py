import random
import string
import json
from os.path import exists
from datetime import datetime
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError,
    MultipleObjectsReturned,
)
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import (
    Product,
    ContactInfo,
    Order,
    OrderProduct,
    Address,
    Payment,
    Invoice,
    Refund,
)
from django.conf import settings
from .forms import CheckoutForm, RefundForm, ShippingSelectForm, CountrySelectForm
from beekeeping_ecommerce.contact.forms import DemoRequestForm
from django.utils.translation import get_language

import stripe


stripe.api_key = settings.STRIPE_API_SECRET_KEY


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


def get_order_product(request, product):
    # check if the order_product exists else send an error message
    try:
        order_product = OrderProduct.objects.get(
            user_id=request.session.session_key,
            ordered=False,
            product=product,
        )
        return order_product
    except ObjectDoesNotExist:
        messages.error(request, _("Le produit n'existe pas dans le panier"))
        return False


def get_order(request):
    # check if the order exists else send an error message
    try:
        order = Order.objects.get(
            user_id=request.session.session_key,
            ordered=False,
        )
        return order
    except ObjectDoesNotExist:
        messages.error(request, _("Le panier n'existe pas"))
        return False


class HomeView(View):
    def get(self, *args, **kwargs):
        form = DemoRequestForm()
        context = self.get_context_data(form)
        return render(self.request, "home.html", context)

    def post(self, *args, **kwargs):
        form = DemoRequestForm(self.request.POST or None)
        if form.is_valid():
            demo_request = form.save()
            context = {"demo_request": demo_request}
            messages.info(self.request, _("Votre demande a bien ??t?? prise en compte."))
            return render(self.request, "contact/confirmation.html", context)
        else:
            context = self.get_context_data(form)
            messages.warning(
                self.request,
                _(
                    "Le formulaire comporte des erreurs, merci de corriger"
                    " et de le soumettre ?? nouveau."
                ),
            )
            return render(self.request, "home.html", context)

    def get_context_data(self, form):
        try:
            order = Order.objects.get(
                user_id=self.request.session.session_key,
                ordered=False,
            )
        except ObjectDoesNotExist:
            order = False
        context = {"order": order, "products": Product.objects.all(), "form": form}
        return context


class CartView(View):
    def get(self, *args, **kwargs):
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")
        form = CountrySelectForm(data={'shipping_country': order.shipping_country})
        context = {
            "order": order,
            "products": order.products.all().order_by("id"),
            "form": form,
            'order_pricea_url': reverse("shop:order_prices"),
            'product_prices_url': reverse("shop:product_prices", kwargs={'product_slug': 'aa'}),
            'select_country_url': reverse("select_country"),
        }
        return render(self.request, "shop/cart.html", context)


class ShippingView(View):
    def get(self, *args, **kwargs):
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")
        form = ShippingSelectForm(destination=order.shipping_country)
        context = {"order": order, "form": form}
        return render(self.request, "shop/shipping.html", context)

    def post(self, *args, **kwargs):
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")
        form = ShippingSelectForm(self.request.POST, destination=order.shipping_country)
        if form.is_valid():
            delivery_option = form.cleaned_data.get("delivery_option")
            order.delivery_option = delivery_option
            order.save()
            return redirect("shop:checkout")
        else:
            context = {"order": order, "form": form}
            return render(self.request, "shop/shipping.html", context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        # Retrieve the the order
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")

        # if the order contains already a billing address, shipping address
        # or customer information and pass it to the form
        data = {}
        if order.shipping_address:
            data.update(
                {
                    "shipping_first_name": order.shipping_address.first_name,
                    "shipping_last_name": order.shipping_address.last_name,
                    "shipping_company_name": order.shipping_address.company_name,
                    "shipping_street_address": order.shipping_address.street_address,
                    "shipping_street_address_line_2": order.shipping_address.street_address_line_2,
                    "shipping_country": order.shipping_address.country,
                    "shipping_zip_code": order.shipping_address.zip_code,
                    "shipping_city": order.shipping_address.city,
                }
            )
        if order.billing_address:
            data.update(
                {
                    "billing_first_name": order.billing_address.first_name,
                    "billing_last_name": order.billing_address.last_name,
                    "billing_company_name": order.billing_address.company_name,
                    "billing_street_address": order.billing_address.street_address,
                    "billing_street_address_line_2": order.billing_address.street_address_line_2,
                    "billing_country": order.billing_address.country,
                    "billing_zip_code": order.billing_address.zip_code,
                    "billing_city": order.billing_address.city,
                }
            )
        if order.contact_info:
            data.update(
                {
                    "phone": order.contact_info.phone,
                    "email": order.contact_info.email,
                }
            )

        if not data:
            form = CheckoutForm(delivery_option=order.delivery_option, order=order)
        else:
            if order.payment_option:
                data.update({"payment_option": order.payment_option})
            if order.delivery_option:
                data.update({"delivery_option": order.delivery_option})
            data.update({"same_billing_address": order.same_billing_address})
            form = CheckoutForm(data, delivery_option=order.delivery_option, order=order)

        context = {"order": order, "form": form}
        return render(self.request, "shop/checkout.html", context)

    def post(self, *args, **kwargs):

        # get the order
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")

        form = CheckoutForm(
            self.request.POST or None, delivery_option=order.delivery_option, order=order
        )

        try:
            same_billing_address = form.fields["same_billing_address"].clean(
                form.data["same_billing_address"]
            )
        except MultiValueDictKeyError:
            same_billing_address = False
        except ValidationError:
            context = {"order": order, "form": form}
            return render(self.request, "shop/checkout.html", context)

        # assign the billing_address fields if same shipping address is selected
        if same_billing_address and order.delivery_option != "R":
            data = {value: self.request.POST[value] for value in self.request.POST}
            data.update(
                {
                    "shipping_first_name": form.data["billing_first_name"],
                    "shipping_last_name": form.data["billing_last_name"],
                    "shipping_company_name": form.data["billing_company_name"],
                    "shipping_street_address": form.data["billing_street_address"],
                    "shipping_street_address_line_2": form.data[
                        "billing_street_address_line_2"
                    ],
                    "shipping_country": form.data["billing_country"],
                    "shipping_zip_code": form.data["billing_zip_code"],
                    "shipping_city": form.data["billing_city"],
                }
            )
            form = CheckoutForm(data, delivery_option=order.delivery_option, order=order)
        if order.delivery_option == "R":
            data = {value: self.request.POST[value] for value in self.request.POST}
            data.update(
                {
                    "shipping_first_name": form.data["billing_first_name"],
                    "shipping_last_name": form.data["billing_last_name"],
                    "shipping_company_name": form.data.get("mr_Nom"),
                    "shipping_street_address": form.data.get("mr_Adresse1"),
                    "shipping_street_address_line_2": form.data.get(
                        "mr_Adresse2"
                    ),
                    "shipping_country": form.data.get("mr_Pays"),
                    "shipping_zip_code": form.data.get("mr_CP"),
                    "shipping_city": form.data.get("mr_Ville"),
                }
            )
            form = CheckoutForm(data, delivery_option=order.delivery_option, order=order)

        if form.is_valid():
            # create ContactInfo object
            contact_info = ContactInfo(
                phone=form.cleaned_data["phone"],
                email=form.cleaned_data["email"],
            )
            if order.contact_info:
                # updates the order.contact_info if it already exists
                contact_info.id = order.contact_info.pk
                contact_info.save()
            else:
                # else create a new one
                contact_info.save()
                order.contact_info = contact_info

            # create a new billing address
            billing_address = Address(
                first_name=form.cleaned_data["billing_first_name"],
                last_name=form.cleaned_data["billing_last_name"],
                company_name=form.cleaned_data["billing_company_name"],
                street_address=form.cleaned_data["billing_street_address"],
                street_address_line_2=form.cleaned_data[
                    "billing_street_address_line_2"
                ],
                country=form.cleaned_data["billing_country"],
                zip_code=form.cleaned_data["billing_zip_code"],
                city=form.cleaned_data["billing_city"],
                address_type="B",
            )
            if order.billing_address:
                # updates the billing address if it already exists
                billing_address.id = order.billing_address.pk
                billing_address.save()
            else:
                # else create a new one
                billing_address.save()
                order.billing_address = billing_address
            
            # create ShippingAddress object
            shipping_address = Address(
                first_name=form.cleaned_data["shipping_first_name"],
                last_name=form.cleaned_data["shipping_last_name"],
                company_name=form.cleaned_data["shipping_company_name"],
                street_address=form.cleaned_data["shipping_street_address"],
                street_address_line_2=form.cleaned_data[
                    "shipping_street_address_line_2"
                ],
                country=form.cleaned_data["shipping_country"],
                zip_code=form.cleaned_data["shipping_zip_code"],
                city=form.cleaned_data["shipping_city"],
            )
            if order.delivery_option == "R":
                order.mondial_relay_id = form.cleaned_data["mr_ID"]
                shipping_address.address_type = "R"
            else:
                order.mondial_relay_id = ""
                shipping_address.address_type = "S"
            if order.shipping_address:
                # updates the shipping address if it already exists
                shipping_address.id = order.shipping_address.pk
                shipping_address.save()
            else:
                # else create a new one
                shipping_address.save()
                order.shipping_address = shipping_address

            # save the payment information and the same_address_information
            order.payment_option = form.cleaned_data["payment_option"]
            order.same_billing_address = form.cleaned_data["same_billing_address"]

            order.save()

            if order.delivery_option == "R" and not order.mondial_relay_id:
                messages.error(
                    self.request, _("Erreur: vous devez s??lectionner un point relais.")
                )
                context = {"order": order, "form": form}
                return render(self.request, "shop/checkout.html", context)

            # check which payment option is selected to redirect to the appropriate view
            if order.payment_option == "S":
                return redirect(
                    reverse("shop:payment", kwargs={"payment_option": "stripe"})
                )
            else:
                messages.warning(
                    self.request,
                    _(
                        "Seul le paiement par carte bancaire est disponible actuellement"
                    ),
                )
                context = {"order": order, "form": form}
                return render(self.request, "shop/checkout.html", context)
        else:
            context = {"order": order, "form": form}
            return render(self.request, "shop/checkout.html", context)


class PaymentView(View):
    def get(self, *args, **kwargs):
        # get the order
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")

        # Convert payment amount to cents for stripe processing
        amount = int(order.get_order_total_price() * 100)  # cents

        # create a stripe payment intent and manage errors
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="eur",
                payment_method_types=[
                    "card",
                ],
            )

        # in case of error, redirect to checkout view
        except stripe.error.CardError as e:
            messages.error(
                self.request, "A payment error occurred: {}".format(e.user_message)
            )
            return redirect("shop:checkout")
        except stripe.error.InvalidRequestError:
            messages.error(self.request, "An invalid request occurred.")
            return redirect("shop:checkout")
        except Exception:
            messages.error(
                self.request,
                _("Erreur interne, votre paiement n'a pas pu ??tre effectu??."),
            )
            return redirect("shop:checkout")
        # else define context and render the view normally
        context = {
            "order": order,
            "client_secret": intent.client_secret,
            "stripe_api_public_key": settings.STRIPE_API_PUBLIC_KEY,
            "payment_redirect_url": self.request.build_absolute_uri(
                reverse("shop:status")
            ),
        }
        return render(self.request, "shop/payment.html", context)


class StatusView(View):
    def get(self, *args, **kwargs):
        # get the order
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")

        # todo: mettre un check sur le paiement pour eviter que la page ne se
        # charge si l'order n'a pas ??t?? pay??

        # Retrieve the payment intent ids returned by stripe after processing the payment
        payment_intent = self.request.GET.get("payment_intent")
        payment_intent_client_secret = self.request.GET.get(
            "payment_intent_client_secret"
        )

        # Retrieve the payment status from stripe API
        payment_intent_obj = stripe.PaymentIntent.retrieve(payment_intent)
        payment_status = payment_intent_obj.status

        # Create a payment object with payment information
        payment = Payment.objects.create(
            stripe_intent_id=payment_intent,
            stripe_client_secret=payment_intent_client_secret,
            amount=int(order.get_order_total_price() * 100),  # cents
            status=payment_status,
        )

        # Update the order with payment information, change ordered status to True
        order.payment = payment
        order.ref_code = create_ref_code()
        order.ordered = True
        order.ordered_date = datetime.now()
        order.save()
        order_products = order.products.all()
        order_products.update(ordered=True)

        # If the payment is sucessful, create an invoice
        if payment_status == "succeeded":
            invoice = Invoice.objects.create()
            messages.info(self.request, _("Votre paiement a ??t?? valid??."))
            order.invoice = invoice
            order.save()
        elif payment_status == "processing":
            messages.warning(
                self.request,
                _(
                    "Votre paiement est en cours de validation."
                    " Nous vous recontacterons lorsque le paiement aura ??t?? valid??"
                ),
            )
        elif payment_status == "requires_payment_method":
            messages.warning(
                self.request, _("Votre paiement a ??chou??. La commande a ??t?? annul??e.")
            )
        else:
            messages.warning(
                self.request, _("Votre paiement a ??chou??. La commande a ??t?? annul??e.")
            )

        # convert stripe timestamp to datetime and amount to eur
        charges = payment_intent_obj.charges.data[0]
        charges_date_created = datetime.fromtimestamp(charges.created)
        amount_charged = charges.amount / 100

        context = {
            "stripe_api_public_key": settings.STRIPE_API_PUBLIC_KEY,
            "payment_status": payment_status,
            "charges": payment_intent_obj.charges.data[0],
            "order": order,
            "date_created": charges_date_created,
            "amount": amount_charged,
            "invoice": invoice,
        }
        return render(self.request, "shop/status.html", context)


def add_to_cart(request, slug):
    # check is the product specified in the url exists
    product = get_object_or_404(Product, slug=slug)

    # if no session is active a session is created
    if not request.session.session_key:
        request.session.create()

    # get or create an order_product and an order
    order_product, is_order_product_created = OrderProduct.objects.get_or_create(
        user_id=request.session.session_key,
        ordered=False,
        product=product,
    )
    order, is_order_created = Order.objects.get_or_create(
        user_id=request.session.session_key,
        ordered=False,
    )

    # update de cart
    if is_order_created or is_order_product_created:
        order.products.add(order_product)
        order.save()
        messages.info(request, _("Le produit a ??t?? ajout?? au panier"))
    else:
        order_product.quantity += 1
        order_product.save()
        messages.info(request, _("Le panier a ??t?? mis ?? jour"))
    return redirect("shop:cart")


def remove_from_cart(request, slug):
    # check is the product specified in the url exists
    product = get_object_or_404(Product, slug=slug)

    order_product = get_order_product(request, product)
    if not order_product:
        return redirect("shop:home")
    order = get_order(request)
    if not order:
        return redirect("shop:home")

    # remove the product from the order
    order_product.delete()
    messages.info(request, _("Le produit a ??t?? supprim?? du panier"))

    # delete the order if it contains no more products
    if not order.products.all().exists():
        order.delete()
        messages.info(request, _("Le panier a ??t?? supprim??"))
        return redirect("shop:home")
    return redirect("shop:cart")


def remove_item_from_cart(request, slug):
    # check is the product specified in the url exists
    product = get_object_or_404(Product, slug=slug)

    order_product = get_order_product(request, product)
    if not order_product:
        return redirect("shop:home")
    order = get_order(request)
    if not order:
        return redirect("shop:home")

    if order_product.quantity == 1:
        order_product.delete()
        messages.info(request, _("Le produit a ??t?? supprim?? du panier"))
    else:
        order_product.quantity -= 1
        order_product.save()
        messages.info(request, _("Le panier a ??t?? mis ?? jour"))
    if not order.products.all().exists():
        order.delete()
        messages.info(request, _("Le panier a ??t?? supprim??"))
        return redirect("shop:home")
    return redirect("shop:cart")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {"form": form}
        return render(self.request, "shop/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")

            try:
                # edit the order
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                Refund.objects.create(order=order, message=message, email=email)
                messages.info(
                    self.request,
                    _("Votre demande de remboursement a bien ??t?? prise en compte."),
                )

                return render(self.request, "shop/request_refund_confirmation.html")
            except ObjectDoesNotExist:
                messages.warning(self.request, _("Ce num??ro de commande n'existe pas."))
            except MultipleObjectsReturned:
                messages.warning(self.request, _("Ce num??ro de commande est invalide."))

            context = {"form": form}
            return render(self.request, "shop/request_refund.html", context)


class ConfidentialityView(View):
    def get(self, *args, **kwargs):
        lang = get_language()
        path = str(settings.APPS_DIR / ("pages/" + lang + "_confidentiality.md"))
        if not exists(path):
            lang = "fr"
        with open(
            str(settings.APPS_DIR / ("pages/" + lang + "_confidentiality.md"))
        ) as f:
            content = f.read()
        context = {"content": content}
        return render(self.request, "shop/confidentiality.html", context)


class LegalTermsView(View):
    def get(self, *args, **kwargs):
        lang = get_language()
        path = str(settings.APPS_DIR / ("pages/" + lang + "_legal_terms.md"))
        if not exists(path):
            lang = "fr"
        with open(str(settings.APPS_DIR / ("pages/" + lang + "_legal_terms.md"))) as f:
            content = f.read()
        context = {"content": content}
        return render(self.request, "shop/legal_terms.html", context)


class SalesConditionsView(View):
    def get(self, *args, **kwargs):
        lang = get_language()
        path = str(settings.APPS_DIR / ("pages/" + lang + "_sales_conditions.md"))
        if not exists(path):
            lang = "fr"
        with open(
            str(settings.APPS_DIR / ("pages/" + lang + "_sales_conditions.md"))
        ) as f:
            content = f.read()
        context = {"content": content}
        return render(self.request, "shop/sales_conditions.html", context)


def select_country_view(request):
    data = json.loads(request.body.decode("utf-8"))
    form = CountrySelectForm(data)
    order = get_order(request)
    if form.is_valid():
        order.shipping_country = form.cleaned_data.get("shipping_country")
        order.save()
    return JsonResponse({"shipping_country": str(order.shipping_country)})


def order_prices_view(request):
    order = get_order(request)
    prices = {
        "order_price_ex_vat": f"{order.get_order_price_ex_vat():.2f} EUR",
        "order_vat_price": f"{order.get_order_vat_price():.2f} EUR",
        "order_price_ex_delivery": f"{order.get_order_price_ex_delivery():.2f} EUR",
        "vat_rate": f"{order.get_vat_rate():.1f} %",
    }
    return JsonResponse(prices)


def product_prices_view(request, product_slug):
    order = get_order(request)
    product = Product.objects.get(slug=product_slug)
    order_product = OrderProduct.objects.get(orders=order, product=product)
    prices = {
        "product_price_incl_vat": f"{product.get_price_incl_vat(order):.2f} EUR",
        "order_product_price": f"{order_product.get_order_product_price():.2f} EUR",
    }
    return JsonResponse(prices)

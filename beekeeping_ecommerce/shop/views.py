import random
import string

from datetime import datetime


from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist, ValidationError, MultipleObjectsReturned
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages

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
from .forms import CheckoutForm, RefundForm
from beekeeping_ecommerce.contact.forms import DemoRequestForm
from django.conf import settings

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
        messages.error(request, "Le produit n'existe pas dans le panier")
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
        messages.error(request, "Le panier n'existe pas")
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
            messages.info(self.request, "Votre demande a bien été prise en compte.")
            return render(self.request, "contact/confirmation.html", context)
        else:
            context = self.get_context_data(form)
            messages.warning(
                self.request,
                "Le formulaire comporte des erreurs, merci de corriger"
                " et de le soumettre à nouveau.",
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
        context = {"order": order, "products": order.products.all().order_by("id")}
        return render(self.request, "shop/cart.html", context)


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
            form = CheckoutForm()
        else:
            if order.payment_option:
                data.update({"payment_option": order.payment_option})
            if order.delivery_option:
                data.update({"delivery_option": order.delivery_option})
            data.update({"same_billing_address": order.same_billing_address})
            form = CheckoutForm(data)

        context = {"order": order, "form": form}
        return render(self.request, "shop/checkout.html", context)

    def post(self, *args, **kwargs):

        # get the order
        order = get_order(self.request)
        if not order:
            return redirect("shop:home")

        form = CheckoutForm(self.request.POST or None)

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
        if same_billing_address:
            data = {value: self.request.POST[value] for value in self.request.POST}
            data.update(
                {
                    "billing_first_name": form.data["shipping_first_name"],
                    "billing_last_name": form.data["shipping_last_name"],
                    "billing_company_name": form.data["shipping_company_name"],
                    "billing_street_address": form.data["shipping_street_address"],
                    "billing_street_address_line_2": form.data[
                        "shipping_street_address_line_2"
                    ],
                    "billing_country": form.data["shipping_country"],
                    "billing_zip_code": form.data["shipping_zip_code"],
                    "billing_city": form.data["shipping_city"],
                }
            )
            form = CheckoutForm(data)

        if form.is_valid():
            # create contact_info object
            contact_info = ContactInfo(
                phone=form.cleaned_data["phone"],
                email=form.cleaned_data["email"],
            )

            # create shipping_address_object
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
                address_type="S",
            )

            # create a new object or update the existing object
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

            # saves or updates the contact_info and the order
            if order.contact_info:
                # updates the shipping address if it already exists
                contact_info.id = order.contact_info.pk
                contact_info.save()
            else:
                # else create a new one
                contact_info.save()
                order.contact_info = contact_info

            # saves or updates the shipping address and the order
            if order.shipping_address:
                # updates the shipping address if it already exists
                shipping_address.id = order.shipping_address.pk
                shipping_address.save()
            else:
                # else create a new one
                shipping_address.save()
                order.shipping_address = shipping_address

            # saves or updates the billing address and the order
            if order.billing_address:
                # updates the billing address if it already exists
                billing_address.id = order.billing_address.pk
                billing_address.save()
            else:
                # else create a new one
                billing_address.save()
                order.billing_address = billing_address

            # save the payment information and the same_address_information
            order.payment_option = form.cleaned_data["payment_option"]
            order.delivery_option = form.cleaned_data["delivery_option"]
            order.same_billing_address = form.cleaned_data["same_billing_address"]

            order.save()

            # check which delivery option is selected to redirect to the appropriate view
            if order.delivery_option != "H":
                messages.warning(
                    self.request, "Seule la livraison à domicile est disponible actuellement"
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
                    self.request, "Seul le paiement par carte bancaire est disponible actuellement"
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
                self.request, "Another problem occurred, maybe unrelated to Stripe."
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
        # charge si l'order n'a pas été payé

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
            messages.info(self.request, "Votre paiement a été validé.")
            order.invoice = invoice
            order.save()
        elif payment_status == "processing":
            messages.warning(
                self.request,
                "Votre paiement est en cours de validation."
                " Nous vous recontacterons lorsque le paiement aura été validé",
            )
        elif payment_status == "requires_payment_method":
            messages.warning(
                self.request, "Votre paiement a échoué. La commande a été annulée."
            )
        else:
            messages.warning(
                self.request, "Votre paiement a échoué. La commande a été annulée."
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
        messages.info(request, "Le produit a été ajouté au panier")
    else:
        order_product.quantity += 1
        order_product.save()
        messages.info(request, "Le panier a été mis à jour")
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
    messages.info(request, "Le produit a été supprimé du panier")

    # delete the order if it contains no more products
    if not order.products.all().exists():
        order.delete()
        messages.info(request, "Le panier a été supprimé")
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
        messages.info(request, "Le produit a été supprimé du panier")
    else:
        order_product.quantity -= 1
        order_product.save()
        messages.info(request, "Le panier a été mis á jour")
    if not order.products.all().exists():
        order.delete()
        messages.info(request, "Le panier a été supprimé")
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
                    "Votre demande de remboursement a bien été prise en compte.",
                )

                return render(self.request, "shop/request_refund_confirmation.html")
            except ObjectDoesNotExist:
                messages.warning(self.request, "Ce numéro de commande n'existe pas.")
            except MultipleObjectsReturned:
                messages.warning(self.request, "Ce numéro de commande est invalide.")

            context = {"form": form}
            return render(self.request, "shop/request_refund.html", context)

from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from django.urls import reverse
from .models import Product, Order, OrderProduct, BillingAddress, Payment, Invoice
from .forms import CheckoutForm
from django.conf import settings

import stripe


stripe.api_key = settings.STRIPE_API_SECRET_KEY


class HomeView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user_id=self.request.session.session_key, ordered=False
            )
        except ObjectDoesNotExist:
            order = False
        context = {"order": order, "products": Product.objects.all()}
        return render(self.request, "home.html", context)


class CartView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user_id=self.request.session.session_key, ordered=False
            )
        except ObjectDoesNotExist:
            messages.info(self.request, "Votre panier est vide.")
            return redirect("shop:home")
        context = {"order": order, "products": order.products.all()}
        return render(self.request, "shop/cart.html", context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        # check if a billing address has already been created for this session
        billing_address_qs = BillingAddress.objects.filter(
                user_id=self.request.session.session_key
            )
        if billing_address_qs.exists():
            billing_address = billing_address_qs[0]
        else:
            billing_address = False
        # Check if the order exists, otherwise return to homepage
        try:
            order = Order.objects.get(
                user_id=self.request.session.session_key, ordered=False
            )
        except ObjectDoesNotExist:
            messages.info(self.request, "Votre panier est vide.")
            return redirect("shop:home")
        # if the order container already a billing address this
        # billing address is passed ot the form
        if order.billing_address:
            form = CheckoutForm(instance=order.billing_address)
        # else the billing address related to the session is
        # passed ot the form
        elif billing_address:
            form = CheckoutForm(instance=billing_address)
        # else the form is blank
        else:
            form = CheckoutForm()
        context = {"order": order, "form": form}
        return render(self.request, "shop/checkout.html", context)

    def post(self, *args, **kwargs):
        
        # check if a billing address has already been created for this session
        billing_address_qs = BillingAddress.objects.filter(
                user_id=self.request.session.session_key
            )
        if billing_address_qs.exists():
            billing_address = billing_address_qs[0]
        else:
            billing_address = False        
        # Check if the order exists, otherwise return to homepage
        try:
            order = Order.objects.get(
                user_id=self.request.session.session_key, ordered=False
            )
        except ObjectDoesNotExist:
            messages.info(self.request, "Votre panier est vide.")
            return redirect("shop:home")
        # Check if the ordercontaines a billing address already
        if order.billing_address:
            billing_address = order.billing_address
        # if a billing address exists from session or existing order, it is assigend to the form
        if billing_address:
            form = CheckoutForm(self.request.POST or None, instance=billing_address)
        else:
            form = CheckoutForm(self.request.POST or None)
        if form.is_valid():
            # create a new object or update the existing object
            billing_address = form.save()
            order.billing_address = billing_address
            order.save()
            # check which payment option is selected to redirect to the appropriate view
            if billing_address.payment_option == "S":
                return redirect(
                    reverse("shop:payment", kwargs={"payment_option": "stripe"})
                )
            else:
                messages.warning(
                    self.request, "Only Stripe payment is available right now"
                )
                return redirect("shop:checkout")


class PaymentView(View):
    def get(self, *args, **kwargs):
        # Check if the order exists, otherwise return to homepage
        try:
            order = Order.objects.get(
                user_id=self.request.session.session_key, ordered=False
            )
        except ObjectDoesNotExist:
            messages.info(self.request, "Votre panier est vide.")
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
        # Check if the order exists, otherwise return to homepage
        try:
            order = Order.objects.get(
                user_id=self.request.session.session_key, ordered=False
            )
        except ObjectDoesNotExist:
            messages.info(self.request, "Votre panier est vide.")
            return redirect("shop:home")

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
            user_id=self.request.session.session_key,
            amount=int(order.get_order_total_price() * 100),  # cents
            status=payment_status,
        )

        # Update the order with payment information, change ordered status to True
        order.payment = payment
        order.ordered = True
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
    if not request.session.session_key:
        request.session.create()
    product = get_object_or_404(Product, slug=slug)
    order_product, is_order_product_created = OrderProduct.objects.get_or_create(
        user_id=request.session.session_key,
        ordered=False,
        product=product,
    )
    order, is_order_created = Order.objects.get_or_create(
        user_id=request.session.session_key,
        ordered=False,
    )
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
    product = get_object_or_404(Product, slug=slug)
    try:
        order_product = OrderProduct.objects.get(
            user_id=request.session.session_key,
            ordered=False,
            product=product,
        )
    except ObjectDoesNotExist:
        messages.info(request, "Le produit n'existe pas dans le panier")
        return redirect("shop:cart")
    try:
        order = Order.objects.get(
            user_id=request.session.session_key,
            ordered=False,
        )
    except ObjectDoesNotExist:
        messages.info(request, "Le panier n'existe pas")
        return redirect("shop:home")
    order_product.delete()
    messages.info(request, "Le produit a été supprimé du panier")
    if not order.products.all().exists():
        order.delete()
        messages.info(request, "Le panier a été supprimé")
    return redirect("shop:cart")


def remove_item_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    try:
        order_product = OrderProduct.objects.get(
            user_id=request.session.session_key,
            ordered=False,
            product=product,
        )
    except ObjectDoesNotExist:
        messages.info(request, "Le produit n'existe pas dans le panier")
        return redirect("shop:cart")
    try:
        order = Order.objects.get(
            user_id=request.session.session_key,
            ordered=False,
        )
    except ObjectDoesNotExist:
        messages.info(request, "Le panier n'existe pas")
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
    return redirect("shop:cart")

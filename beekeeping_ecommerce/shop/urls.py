from django.urls import path
from django.views.generic import TemplateView

from .views import (
    HomeView,
    CartView,
    add_to_cart,
    remove_from_cart,
    remove_item_from_cart,
    ShippingView,
    CheckoutView,
    PaymentView,
    StatusView,
    RequestRefundView,
)


app_name = "shop"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("cart/", CartView.as_view(), name="cart"),
    path("add-to-cart/<slug>", add_to_cart, name="add-to-cart"),
    path("remove-from-cart/<slug>", remove_from_cart, name="remove-from-cart"),
    path(
        "remove-item-from-cart/<slug>",
        remove_item_from_cart,
        name="remove-item-from-cart",
    ),
    path("shipping/", ShippingView.as_view(), name="shipping"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("payment/<payment_option>", PaymentView.as_view(), name="payment"),
    path("status/", StatusView.as_view(), name="status"),
    path("request-refund/", RequestRefundView.as_view(), name="request-refund"),
    path(
        "sales-conditions",
        TemplateView.as_view(template_name="shop/sales_conditions.html"),
        name="sales-conditions",
    ),
    path(
        "contact/",
        TemplateView.as_view(template_name="shop/contact.html"),
        name="contact",
    ),
    path(
        "legal-terms/",
        TemplateView.as_view(template_name="shop/legal_terms.html"),
        name="legal-terms",
    ),
    path(
        "confidentiality/",
        TemplateView.as_view(template_name="shop/confidentiality.html"),
        name="confidentiality",
    ),
]

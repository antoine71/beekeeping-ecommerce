from django.urls import path

from .views import (
    HomeView,
    CartView,
    add_to_cart,
    remove_from_cart,
    remove_item_from_cart,
    CheckoutView,
    PaymentView,
    StatusView
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
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("payment/<payment_option>", PaymentView.as_view(), name="payment"),
    path("status/", StatusView.as_view(), name="status"),

]

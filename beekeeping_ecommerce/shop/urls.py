from django.urls import path
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

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
    ConfidentialityView,
    LegalTermsView,
    SalesConditionsView
)


app_name = "shop"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path(_("panier/"), CartView.as_view(), name="cart"),
    path(_("ajouter-au-panier/<slug>"), add_to_cart, name="add-to-cart"),
    path(_("supprimer-du-panier/<slug>"), remove_from_cart, name="remove-from-cart"),
    path(
        _("enlever-un-element-du-panier/<slug>"),
        remove_item_from_cart,
        name="remove-item-from-cart",
    ),
    path(_("expedition/"), ShippingView.as_view(), name="shipping"),
    path(_("informations/"), CheckoutView.as_view(), name="checkout"),
    path(_("paiement/<payment_option>"), PaymentView.as_view(), name="payment"),
    path(_("status/"), StatusView.as_view(), name="status"),
    path(_("remboursement/"), RequestRefundView.as_view(), name="request-refund"),
    path(
        _("conditions-generales-de-vente"),
        SalesConditionsView.as_view(),
        name="sales-conditions",
    ),
    path(
        _("contact/"),
        TemplateView.as_view(template_name="shop/contact.html"),
        name="contact",
    ),
    path(
        _("mentions-legales/"),
        LegalTermsView.as_view(),
        name="legal-terms",
    ),
    path(
        _("confidentialite/"),
        ConfidentialityView.as_view(),
        name="confidentiality",
    ),

]

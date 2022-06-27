from email.policy import default
from random import choices
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field

from .models import Address

from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField


PAYMENT_CHOICES = (
    ("S", "Stripe"),
    ("P", "Paypal"),
)


class CheckoutForm(forms.Form):

    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    company_name = forms.CharField(
        label="Société", help_text="optionnel", required=False
    )
    phone = forms.CharField(label="Numéro de téléphone")
    email = forms.EmailField(label="Adresse Email")
    street_address = forms.CharField(label="Adresse")
    street_address_line_2 = forms.CharField(
        label="Complément d'Adresse", help_text="optionnel", required=False
    )
    country = CountryField().formfield(label="Prénom", widget=CountrySelectWidget())
    zip_code = forms.CharField(label="Code Postal")
    city = forms.CharField(label="Ville")
    same_shipping_address = forms.BooleanField(
        label="L'adresse de livraison est identique à l'adresse de facturation"
    )
    payment_option = forms.ChoiceField(label="Options de paiement", choices=PAYMENT_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Saisissez vos informations de contact",
                Div("first_name", "last_name", css_class="inline-form-wrapper"),
                "company_name",
                Div("phone", "email", css_class="inline-form-wrapper"),
            ),
            Fieldset(
                "Saisissez votre adresse de Livraison",
                "street_address",
                "street_address_line_2",
                Div("zip_code", "city", css_class="inline-form-wrapper"),
                "country",
                Div("same_shipping_address", css_class="custom-form-checkbox"),
            ),
            Fieldset(
                "Sélectionnez un moyen de paiement",
                "payment_option",
            ),
        )
        self.helper.add_input(
            Submit("submit", "Commander", css_class="btn-primary btn-primary_center")
        )
        self.helper.form_method = "post"


class RefundForm(forms.Form):
    ref_code = forms.CharField(label="Numéro de référence de la commande")
    email = forms.EmailField(label="Adresse Email")
    message = forms.CharField(
        label="Message décrivant la ou les raisons de votre demande de remboursement:",
        widget=forms.Textarea(attrs={"rows": 6}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit("submit", "Commander", css_class="btn-primary btn-primary_center")
        )
        self.helper.form_method = "post"

from django import forms
from django.db import models

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field


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
    shipping_street_address = forms.CharField(label="Adresse")
    shipping_street_address_line_2 = forms.CharField(
        label="Complément d'Adresse", help_text="optionnel", required=False
    )
    shipping_country = CountryField().formfield(label="Pays")
    shipping_zip_code = forms.CharField(label="Code Postal")
    shipping_city = forms.CharField(label="Ville")
    billing_street_address = forms.CharField(label="Adresse")
    billing_street_address_line_2 = forms.CharField(
        label="Complément d'Adresse", help_text="optionnel", required=False
    )
    billing_country = CountryField().formfield(label="Pays")
    billing_zip_code = forms.CharField(label="Code Postal")
    billing_city = forms.CharField(label="Ville")
    same_billing_address = forms.BooleanField(
        label="L'adresse de facturation est identique à l'adresse de livraison",
        required=False,
        initial=True,
    )
    payment_option = forms.ChoiceField(
        label="Options de paiement", choices=PAYMENT_CHOICES
    )

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
                "shipping_street_address",
                "shipping_street_address_line_2",
                Div(
                    "shipping_zip_code",
                    "shipping_city",
                    css_class="inline-form-wrapper",
                ),
                "shipping_country",
            ),
            Div(
                "same_billing_address",
                css_class="custom-form-checkbox",
            ),
            Fieldset(
                "Saisissez votre adresse de Facturation",
                "billing_street_address",
                "billing_street_address_line_2",
                Div("billing_zip_code", "billing_city", css_class="inline-form-wrapper"),
                "billing_country",
                css_class="hideable-shipping-form",
            ),
            Fieldset(
                "Sélectionnez un moyen de paiement",
                "payment_option",
            ),
        )
        self.helper.add_input(
            Submit("submit", "Commander", css_class="btn-primary btn-primary_center")
        )


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

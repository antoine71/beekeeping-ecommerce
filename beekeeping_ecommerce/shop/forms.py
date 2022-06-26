from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field

from .models import BillingAddress

# from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ("S", "Stripe"),
    ("P", "Paypal"),
)


class CheckoutForm(forms.ModelForm):
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
                "same_shipping_address",
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

    class Meta:
        model = BillingAddress
        fields = [
            "first_name",
            "last_name",
            "company_name",
            "street_address",
            "street_address_line_2",
            "country",
            "zip_code",
            "city",
            "same_shipping_address",
            "payment_option",
            "email",
            "phone",
        ]

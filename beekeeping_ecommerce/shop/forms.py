from django import forms
from django_countries.fields import CountryField

from .models import BillingAddress

# from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ("S", "Stripe"),
    ("P", "Paypal"),
)


# class CheckoutForm(forms.Form):
#     first_name = forms.CharField(label="Prénom")
#     last_name = forms.CharField(label="Nom")
#     company_name = forms.CharField(label="Société (optionnel)", required=False)
#     street_address = forms.CharField(label="Adresse")
#     street_address_line_2 = forms.CharField(
#         label="Complément d'adresse (optionnel)", required=False
#     )
#     country = CountryField(blank_label="(choisissez le pays)").formfield()
#     zip_code = forms.CharField(label="Code postal")
#     city = forms.CharField(label="Ville")
#     same_shipping_address = forms.BooleanField(
#         label="L'adresse d'expédition est identique à l'adresse de facturation",
#         widget=forms.CheckboxInput(attrs={"class": "form__group_checkbox"}),
#         required=False,
#     )
#     payment_option = forms.ChoiceField(
#         widget=forms.RadioSelect(), choices=PAYMENT_CHOICES, label="Options de payment"
#     )

class CheckoutForm(forms.ModelForm):
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
        ]
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div
from django_countries.fields import CountryField

from .models import DELIVERY_CHOICES, PAYMENT_CHOICES


class ShippingSelectForm(forms.Form):
    delivery_option = forms.ChoiceField(
        label="", choices=DELIVERY_CHOICES, widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Choisissez un mode de livraison"),
                "delivery_option",
            )
        )
        self.helper.add_input(
            Submit("submit", _("Envoyer"), css_class="btn-primary btn-primary_center")
        )
        self.helper.form_method = "post"


class CheckoutForm(forms.Form):

    phone = forms.CharField(label=_("Numéro de téléphone"))
    email = forms.EmailField(label=_("Adresse Email"))
    shipping_first_name = forms.CharField(label=_("Prénom"))
    shipping_last_name = forms.CharField(label=_("Nom"))
    shipping_company_name = forms.CharField(
        label=_("Société"), help_text="optionnel", required=False
    )
    shipping_street_address = forms.CharField(label=_("Adresse"))
    shipping_street_address_line_2 = forms.CharField(
        label=_("Complément d'Adresse"), help_text="optionnel", required=False
    )
    shipping_country = CountryField().formfield(label=_("Pays"))
    shipping_zip_code = forms.CharField(label=_("Code Postal"))
    shipping_city = forms.CharField(label=_("Ville"))
    billing_first_name = forms.CharField(label=_("Prénom"))
    billing_last_name = forms.CharField(label=_("Nom"))
    billing_company_name = forms.CharField(
        label=_("Société"), help_text="optionnel", required=False
    )
    billing_street_address = forms.CharField(label=_("Adresse"))
    billing_street_address_line_2 = forms.CharField(
        label=_("Complément d'Adresse"), help_text="optionnel", required=False
    )
    billing_country = CountryField().formfield(label=_("Pays"))
    billing_zip_code = forms.CharField(label=_("Code Postal"))
    billing_city = forms.CharField(label=_("Ville"))
    same_billing_address = forms.BooleanField(
        label=_("L'adresse de livraison est identique à l'adresse de facturation"),
        required=False,
        initial=True,
    )
    payment_option = forms.ChoiceField(
        label=_("Options de paiement"), choices=PAYMENT_CHOICES
    )
    accept_confidentiality = forms.BooleanField(
        label=_("J'accepte la politique de confidentialité et de traitement"
                " des données personnelles"),
        initial=False,
    )
    mr_ID = forms.CharField(required=False)
    mr_Nom = forms.CharField(required=False)
    mr_Adresse1 = forms.CharField(required=False)
    mr_Adresse2 = forms.CharField(required=False)
    mr_CP = forms.CharField(required=False)
    mr_Ville = forms.CharField(required=False)
    mr_Pays = forms.CharField(required=False)

    home_shipping_fieldset = Fieldset(
        _("Saisissez vos informations de livraison"),
        "phone",
        Div(
            "same_billing_address",
            css_class="custom-form-checkbox",
        ),
        Div(
            Div(
                "shipping_first_name",
                "shipping_last_name",
                css_class="inline-form-wrapper",
            ),
            "shipping_company_name",
            "shipping_street_address",
            "shipping_street_address_line_2",
            Div(
                "shipping_zip_code",
                "shipping_city",
                css_class="inline-form-wrapper",
            ),
            "shipping_country",
            css_id="hideable-shipping-form",
        ),
    )

    mondial_relay_shipping_fieldset = Fieldset(
        _("Saisissez vos informations de livraison"),
        "phone",
        Div(css_id="Zone_Widget"),
    )

    def __init__(self, *args, delivery_option="", **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Saisissez vos informations de contact"),
                "email",
            ),
            Fieldset(
                _("Saisissez votre adresse de Facturation"),
                Div(
                    "billing_first_name",
                    "billing_last_name",
                    css_class="inline-form-wrapper",
                ),
                "billing_company_name",
                "billing_street_address",
                "billing_street_address_line_2",
                Div(
                    "billing_zip_code", "billing_city", css_class="inline-form-wrapper"
                ),
                "billing_country",
            ),
            Fieldset(
                _("Sélectionnez un moyen de paiement"),
                "payment_option",
            ),
            Div("accept_confidentiality", css_class="custom-form-checkbox"),
        )
        self.helper.add_input(
            Submit("submit", _("Commander"), css_class="btn-primary btn-primary_center")
        )
        if delivery_option == 'H':
            self.helper.layout.fields.insert(-2, CheckoutForm.home_shipping_fieldset)
        elif delivery_option == 'R':
            self.helper.layout.fields.insert(-2, CheckoutForm.mondial_relay_shipping_fieldset)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     mr_ID = cleaned_data.get("mr_ID")
    #     delivery_option = cleaned_data.get("delivery_option")

    #     if delivery_option == "R" and (not mr_ID or mr_ID == "null"):
    #         raise ValidationError("Vous devez sélectionner un point relais")


class MondialRelayForm(forms.Form):
    mr_ID = forms.CharField(required=False)
    mr_Nom = forms.CharField(required=False)
    mr_Adresse1 = forms.CharField(required=False)
    mr_Adresse2 = forms.CharField(required=False)
    mr_CP = forms.CharField(required=False)
    mr_Ville = forms.CharField(required=False)
    mr_Pays = forms.CharField(required=False)


class RefundForm(forms.Form):
    ref_code = forms.CharField(label=_("Numéro de référence de la commande"))
    email = forms.EmailField(label=_("Adresse Email"))
    message = forms.CharField(
        label=_("Message décrivant la ou les raisons de votre demande de remboursement:"),
        widget=forms.Textarea(attrs={"rows": 6}),
    )
    accept_conditions = forms.BooleanField(
        label=_("J'accepte les conditions s'appliquant à l'exercice du droit de rétractation "
                "mentionnées dans les conditions générales de ventes"),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "ref_code",
            "email",
            "message",
            Div("accept_conditions", css_class="custom-form-checkbox"),
            Div(
                css_class="g-recaptcha",
                **{"data-sitekey": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"}
            ),
        )
        self.helper.add_input(
            Submit("submit", _("Envoyer"), css_class="btn-primary btn-primary_center")
        )
        self.helper.form_method = "post"

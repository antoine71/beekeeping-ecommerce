from django import forms
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div

from .models import DemoRequest


class DemoRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Saisissez le nom et la ville du magasin"),
                "shop_name",
                Div("post_code", "city", css_class="inline-form-wrapper"),
            ),
            Fieldset(
                _("Comment pouvons nous vous prévenir de la démonstration ?"),
                "email",
                Div("accept_conditions", css_class="custom-form-checkbox"),
            ),
            Div(
                css_class="g-recaptcha",
                **{"data-sitekey": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"}
            ),
        )
        self.helper.add_input(
            Submit(
                "submit",
                _("Demander une Démonstration"),
                css_class="btn-primary btn-primary_center",
            )
        )
        self.helper.form_method = "post"

    class Meta:
        model = DemoRequest

        fields = [
            "shop_name",
            "city",
            "post_code",
            "email",
            "accept_conditions",
        ]

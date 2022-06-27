from django import forms

from .models import DemoRequest

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field


class DemoRequestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Saisissez le nom et la ville du magasin",
                "shop_name",
                Div("post_code", "city", css_class="inline-form-wrapper"),
            ),
            Fieldset(
                "Comment pouvons nous vous joindre ?",
                Div("first_name", "last_name", css_class="inline-form-wrapper"),
                Div("email", "phone", css_class="inline-form-wrapper"),
                Div("accept_conditions", css_class="custom-form-checkbox"),
            ),
            Fieldset(
                "A quelle date souhaitez-vous que la démonstration ait lieu ?",
                Field("requested_date", placeholder="24/08/2022"),
            ),
        )
        self.helper.add_input(Submit('submit', 'Demander une Démonstration', css_class="btn-primary btn-primary_center"))
        self.helper.form_method = 'post'

    class Meta:
        model = DemoRequest

        fields = [
            "shop_name",
            "city",
            "post_code",
            "requested_date",
            "last_name",
            "first_name",
            "email",
            "phone",
            "accept_conditions",
        ]
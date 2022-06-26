from django import forms

from .models import DemoRequest


class DemoRequestForm(forms.ModelForm):

    class Meta:
        model = DemoRequest
        fields = [
            'shop_name',
            'city',
            'post_code',
            'requested_date',
            'last_name',
            'first_name',
            'email',
            'phone',
            'accept_conditions',
        ]

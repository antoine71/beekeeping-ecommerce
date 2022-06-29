import datetime

from django.db import models
from django.core.exceptions import ValidationError


def validate_confidentiality(value):
    if not value:
        raise ValidationError("Vous devez accepter la politique de confidentialité")


def validate_date_requested(value):
    if value < datetime.datetime.now().date():
        raise ValidationError("La date saisie est déjà passée")


class DemoRequest(models.Model):
    shop_name = models.CharField("Nom du Magasin", max_length=255)
    city = models.CharField("Ville", max_length=100)
    post_code = models.CharField("Code Postal", max_length=10)
    email = models.EmailField("Adresse Email")
    accept_conditions = models.BooleanField(
        "Accepter la politique de confidentialité",
        validators=[validate_confidentiality],
    )
    date_created = models.DateTimeField("Date de création", auto_now_add=True)

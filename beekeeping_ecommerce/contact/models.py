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
    requested_date = models.DateField(
        "Date souhaitée",
        help_text=("au format jj/mm/aaaa"),
        validators=[validate_date_requested]
    )
    last_name = models.CharField("Nom de Famille", max_length=100)
    first_name = models.CharField("Prénom", max_length=100)
    email = models.EmailField("Adresse Email")
    phone = models.CharField("Numéro de téléphone", max_length=20)
    accept_conditions = models.BooleanField(
        "Accepter la politique de confidentialité",
        validators=[validate_confidentiality],
    )
    date_created = models.DateTimeField("Date de création", auto_now_add=True)
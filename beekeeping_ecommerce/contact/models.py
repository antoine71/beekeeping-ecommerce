import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_confidentiality(value):
    if not value:
        raise ValidationError(_("Vous devez accepter la politique de confidentialité"))


def validate_date_requested(value):
    if value < datetime.datetime.now().date():
        raise ValidationError(_("La date saisie est déjà passée"))


class DemoRequest(models.Model):
    shop_name = models.CharField(_("Nom du Magasin"), max_length=255)
    city = models.CharField(_("Ville"), max_length=100)
    post_code = models.CharField(_("Code Postal"), max_length=10)
    email = models.EmailField(_("Adresse Email"))
    accept_conditions = models.BooleanField(
        _("Accepter la politique de confidentialité"),
        validators=[validate_confidentiality],
    )
    date_created = models.DateTimeField(_("Date de création"), auto_now_add=True)

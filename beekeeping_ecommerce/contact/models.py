from django.db import models


class DemoRequest(models.Model):
    shop_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    post_code = models.CharField(max_length=10)
    requested_date = models.DateField()
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    accept_conditions = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)

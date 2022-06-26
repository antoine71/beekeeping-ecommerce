from django.db import models
from django.conf import settings

from autoslug import AutoSlugField


class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = AutoSlugField(unique=True, always_update=False, populate_from="title")
    language = models.CharField(max_length=2, null=True, blank=True)
    abstract = models.CharField(max_length=512)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.title}'

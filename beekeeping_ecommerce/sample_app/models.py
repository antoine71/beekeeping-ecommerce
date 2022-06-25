from django.db import models
from django.conf import settings

from autoslug import AutoSlugField

### register your mnodels here - see example below

# class Article(models.Model):
#     title = models.CharField(max_length=255)
#     slug = AutoSlugField(unique=True, always_update=False, populate_from="title")
#     abstract = models.TextField(max_length=512)
#     content = models.TextField(max_length=2048)
#     date_created = models.DateTimeField(auto_now_add=True)
#     author = models.ForeignKey(
#         to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

#     def __str__(self):
#         return f'{self.title}'
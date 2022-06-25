from typing import Any, Sequence

from factory import post_generation, SubFactory, Faker
from factory.django import DjangoModelFactory

from django.contrib.auth import get_user_model

## import your models below
# from ..models import Article


### Create your factories - see example below

# class UserFactory(DjangoModelFactory):

#     username = Faker('user_name')
#     email = Faker('email')
#     first_name = Faker('first_name')
#     last_name = Faker('last_name')

#     @post_generation
#     def password(self, create: bool, extracted: Sequence[Any], **kwargs):
#         password = (
#             extracted
#             if extracted
#             else Faker(
#                 "password",
#                 length=42,
#                 special_chars=True,
#                 digits=True,
#                 upper_case=True,
#                 lower_case=True,
#             ).evaluate(None, None, extra={"locale": None})
#         )
#         self.set_password(password)

#     class Meta:
#         model = get_user_model()
#         django_get_or_create = ["username"]


# class ArticleFactory(DjangoModelFactory):

#     class Meta:
#         model = Article

#     title = Faker('text', max_nb_chars=255)
#     abstract = Faker('text', max_nb_chars=512)
#     content = Faker('text', max_nb_chars=512)
#     author = SubFactory(UserFactory)

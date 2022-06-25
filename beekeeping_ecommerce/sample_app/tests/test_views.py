import pytest

from . import factories
from .. import views


pytestmark = pytest.mark.django_db


### write your views tests - see examples below

# def test_index_view(rf):
#     factories.ArticleFactory(title='first title')
#     factories.ArticleFactory(title='second title')
#     factories.ArticleFactory(title='third title')

#     response = views.index(rf)

#     assert response.status_code == 200
#     assert b'first title' in response.content
#     assert b'second title' in response.content
#     assert b'third title' in response.content


# def test_article_view(rf):
#     factories.ArticleFactory(
#         title='This is the title',
#         content='This is the content',
#     )
#     response = views.article(rf, 'this-is-the-title')

#     assert response.status_code == 200
#     assert b'This is the content' in response.content
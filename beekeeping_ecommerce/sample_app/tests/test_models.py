import pytest

from . import factories


pytestmark = pytest.mark.django_db

### write your model tests - see example below

# def test_article():
#     article = factories.ArticleFactory(
#         title='my article title',
#     )
#     assert str(article) == 'my article title'
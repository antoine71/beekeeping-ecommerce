from django.urls import resolve, reverse


## Write your url tests - see example below

# def test_index():
#     assert reverse('blog:index') == '/blog/'
#     assert resolve('/blog/').view_name == 'blog:index'


# def test_address():
#     assert reverse(
#         'blog:article',
#         kwargs={'slug': 'this-is-a-slug'}
#     ) == '/blog/this-is-a-slug/'
#     assert resolve('/blog/this-is-a-slug/').view_name == 'blog:article'
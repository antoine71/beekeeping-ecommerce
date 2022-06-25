from operator import attrgetter
from django.shortcuts import render
from django.core.paginator import Paginator

### import your models
# from .models import Article

### define your views here - see example below

# def index(request):
#     articles = Article.objects.all().order_by('-date_created')
    
#     paginator = Paginator(articles, 5)
#     try:
#         page_number = request.GET.get('page')
#     except AttributeError:
#         page_number = 1
#     page_obj = paginator.get_page(page_number)
    
#     context = {
#         "articles": articles,
#         "page_obj": page_obj,        
#     }
#     return render(request, "blog/index.html", context)


# def article(request, slug):
#     article = Article.objects.get(slug=slug)
#     context = {
#         "article": article
#     }
#     return render(request, "blog/article.html", context)
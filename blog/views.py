from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.models import Article


def home(request):
    context = {
        'articles': paginate_articles(request, 5)
    }
    return render(request, 'blog/index.html', context)


def articles(request):
    context = {
        'articles': paginate_articles(request, 1)
    }
    return render(request, 'blog/articles.html', context)


def article_detail(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True
    )
    return render(request, 'blog/article_detail.html', {'article': article})


def paginate_articles(request, items):
    article_list = Article.objects.filter(
        is_published=True
    ).order_by('-publication_date')
    paginator = Paginator(article_list, items)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles = paginator.page(paginator.num_pages)
    return articles

from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView

from blog.models import Article, CustomUser
from blog.utils import STATUS_CHOICES, has_enough_privileges
from google.appengine.api import users


class ArticleListView(ListView):
    model = Article
    template_name = "blog/articles.html"
    context_object_name = 'articles'
    paginate_by = 5
    queryset = Article.objects.filter(status=STATUS_CHOICES['Published'])


class HomeArticleListView(ArticleListView):
    paginate_by = 3
    template_name = 'blog/index.html'


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.status == STATUS_CHOICES['Published']:
        return render(request, 'blog/article_detail.html', {'article': article})
    else:
        if request.user.is_authenticated():
            if has_enough_privileges(request.user.role, 'Editor') or article.author == request.user:
                return render(request, 'blog/article_detail.html', {'article': article, 'private': True})
    raise Http404()


def user_detail(request, slug):
    user = get_object_or_404(
        CustomUser,
        slug=slug,
    )
    return render(request, 'blog/user_detail.html', {'target_user': user})


def logout(request):
    return HttpResponseRedirect(users.create_logout_url(dest_url=reverse('home')))

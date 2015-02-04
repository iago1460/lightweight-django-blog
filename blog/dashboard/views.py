import datetime

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from blog.dashboard.decorators import login_required, has_permission_level
from blog.dashboard.forms import UserForm, ConfigurationForm, ProfileForm,\
    ArticleForm, ArticleAuthorForm, ArticleContributorForm, AddUserForm
from blog.dashboard.models import SiteConfiguration
from blog.models import CustomUser, Article
from blog.utils import has_enough_privileges, has_changed, STATUS_CHOICES,\
    ROLE_CHOICES
from django.http.response import Http404


@login_required
def index(request):
    context = {
        'published_articles': get_articles_queryset(request.user).filter(status=STATUS_CHOICES['Published']).count(),
        'pending_articles': get_articles_queryset(request.user).filter(status=STATUS_CHOICES['Pending']).count(),
        'draft_articles': get_articles_queryset(request.user).filter(status=STATUS_CHOICES['Draft']).count(),
        'users': CustomUser.objects.all().count(),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
@has_permission_level(group_name='Contributor')
def edit_profile(request):
    user = request.user
    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return render(request, "dashboard/edit_profile.html", {'form': form, 'saved': True})
    return render(request, "dashboard/edit_profile.html", {'form': form})


@login_required
@has_permission_level(group_name='Administrator')
def edit_settings(request):
    configuration = SiteConfiguration.get_global()
    form = ConfigurationForm(instance=configuration)
    if request.method == 'POST':
        form = ConfigurationForm(request.POST, instance=configuration)
        if form.is_valid():
            form.save()
            return render(request, "dashboard/edit_settings.html", {'form': form, 'saved': True})
    return render(request, "dashboard/edit_settings.html", {'form': form})


class UserListView(ListView):
    model = CustomUser
    template_name = "dashboard/all_users.html"
    context_object_name = 'user_list'
    paginate_by = 10
    queryset = CustomUser.objects.order_by('email')

    @method_decorator(login_required)
    @method_decorator(has_permission_level(group_name='Administrator'))
    def dispatch(self, request, *args, **kwargs):
        return super(UserListView, self).dispatch(request, *args, **kwargs)


@login_required
@has_permission_level(group_name='Administrator')
def add_user(request):
    if request.method == 'GET':
        form = AddUserForm()
    else:
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:users')
    return render(request, "dashboard/add_user.html", {'form': form})


@login_required
@has_permission_level(group_name='Administrator')
def edit_user(request, pk):
    user = get_object_or_404(
        CustomUser,
        pk=pk
    )
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return render(request, "dashboard/edit_user.html", {'form': form, 'target_user': user, 'saved': True})
    return render(request, "dashboard/edit_user.html", {'form': form, 'target_user': user})


class DeleteUserView(DeleteView):
    model = CustomUser
    template_name = "dashboard/delete_user.html"
    success_url = reverse_lazy('dashboard:users')

    @method_decorator(login_required)
    @method_decorator(has_permission_level(group_name='Administrator'))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteUserView, self).dispatch(request, *args, **kwargs)


def get_articles_queryset(user):
    if has_enough_privileges(user.role, 'Editor'):
        queryset = Article.objects.all()
    else:
        queryset = Article.objects.filter(author=user)
    return queryset


class ArticleListView(ListView):
    model = Article
    template_name = "dashboard/article_list.html"
    context_object_name = 'article_list'
    paginate_by = 10
    additional_context = {
        'heading': _('All Articles'),
        'show_status': True,
        'all_articles': True
    }

    def get_queryset(self):
        queryset = get_articles_queryset(self.request.user)
        return queryset.order_by('-creation_date')

    def get_context_data(self, *args, **kwargs):
        context = super(ArticleListView, self).get_context_data(
            *args, **kwargs)
        return dict(context.items() + self.additional_context.items())

    @method_decorator(login_required)
    @method_decorator(has_permission_level(group_name='Contributor'))
    def dispatch(self, request, *args, **kwargs):
        return super(ArticleListView, self).dispatch(request, *args, **kwargs)


class ArticleDraftListView(ArticleListView):
    additional_context = {
        'heading': _('All Draft Articles'),
        'draft_articles': True
    }

    def get_queryset(self):
        return super(ArticleDraftListView, self).get_queryset().filter(status=STATUS_CHOICES['Draft'])


class ArticlePublishedListView(ArticleListView):
    additional_context = {
        'heading': _('All Published Articles'),
        'published_articles': True
    }

    def get_queryset(self):
        return super(ArticlePublishedListView, self).get_queryset().filter(status=STATUS_CHOICES['Published'])


class ArticlePendingListView(ArticleListView):
    additional_context = {
        'heading': _('All Pending Articles'),
        'pending_articles': True
    }

    def get_queryset(self):
        return super(ArticlePendingListView, self).get_queryset().filter(status=STATUS_CHOICES['Pending'])


@login_required
@has_permission_level(group_name='Contributor')
def add_article(request):
    if request.method == 'GET':
        form = get_article_form(request.user)
    else:
        form = get_article_form(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:articles')
    return render(request, "dashboard/add_article.html", {'form': form})


@login_required
@has_permission_level(group_name='Contributor')
def edit_article(request, pk):
    article = get_object_or_404(
        Article,
        pk=pk
    )
    # Only Editors or Admis can edit other articles
    if not has_enough_privileges(request.user.role, 'Editor') and article.author != request.user:
        raise Http404()

    # Contributors can't change articles if its are pusblished
    if article.is_published and request.user.role == ROLE_CHOICES['Contributor']:
        raise Http404()

    form = get_article_form(request_user=request.user, instance=article)
    if request.method == 'POST':
        form = get_article_form(
            request_user=request.user, instance=article, data=request.POST)
        if form.is_valid():
            new_article = form.save(commit=False)
            if form.cleaned_data['status'] == STATUS_CHOICES['Published'] and has_changed(article, 'status'):
                new_article.publication_date = datetime.datetime.now()
            new_article.save()
            return render(request, "dashboard/edit_article.html", {'form': form, 'article': article, 'saved': True})
    return render(request, "dashboard/edit_article.html", {'form': form, 'article': article})


def get_article_form(request_user, *args, **kwargs):
    if has_enough_privileges(request_user.role, 'Editor'):
        return ArticleForm(request_user, *args, **kwargs)
    if has_enough_privileges(request_user.role, 'Author'):
        return ArticleAuthorForm(request_user, *args, **kwargs)
    else:
        return ArticleContributorForm(request_user, *args, **kwargs)


class DeleteArticleView(DeleteView):
    model = Article
    template_name = "dashboard/delete_article.html"
    success_url = reverse_lazy('dashboard:articles')

    @method_decorator(login_required)
    @method_decorator(has_permission_level(group_name='Author'))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteArticleView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(DeleteArticleView, self).get_queryset()
        if self.request.user.role == ROLE_CHOICES['Author']:
            return qs.filter(author=self.request.user)
        return qs

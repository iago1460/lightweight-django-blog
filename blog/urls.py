from django.conf.urls import patterns, include, url
from django.contrib import admin
import session_csrf

from blog import views
session_csrf.monkeypatch()

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        views.HomeArticleListView.as_view(),
        name='home'
        ),
    url(r'^articles/$',
        views.ArticleListView.as_view(),
        name='articles'
        ),
    url(r'^articles/(?P<slug>[-\w]+)/$',
        views.article_detail,
        name='article_detail'
        ),
    url(r'^users/(?P<slug>[-\w]+)/$',
        views.user_detail,
        name='user_detail'
        ),
    # testing
    #     url(r'^admin/',
    #         include(admin.site.urls)
    #         ),
    url(r'^dashboard/',
        include('blog.dashboard.urls', namespace="dashboard")
        ),
    url(r'^logout/$',
        views.logout,
        name='logout'
        ),
    url(r'^_ah/',
        include('djangae.urls')
        ),
)


# DEBUG
from blog import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

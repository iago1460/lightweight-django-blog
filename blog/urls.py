from django.conf.urls import patterns, include, url

import session_csrf
session_csrf.monkeypatch()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'blog.views.home', name='home'),
    url(r'^articles/$', 'blog.views.articles', name='articles'),
    url(r'^articles/(?P<slug>[-\w]+)/$',
        'blog.views.article_detail', name='article_detail'),

    url(r'^_ah/', include('djangae.urls')),

    # Note that by default this is also locked down with login:admin in
    # app.yaml
    url(r'^admin/', include(admin.site.urls)),
)


# DEBUG
from django.conf import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)

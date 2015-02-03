from djangae.contrib.gauth.models import GaeAbstractBaseUser, PermissionsMixin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from blog import settings
from blog.utils import STATUS_CHOICES, ROLE_CHOICES, unique_slug


class Article(models.Model):

    STATUS_CHOICES_TUPLE = (
        (STATUS_CHOICES['Draft'], _('Draft')),
        (STATUS_CHOICES['Pending'], _('Pending Review')),
        (STATUS_CHOICES['Published'], _('Published'))
    )

    status = models.IntegerField(
        verbose_name=_('Status'),
        choices=STATUS_CHOICES_TUPLE,
        default=STATUS_CHOICES['Draft']
    )

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=255,
    )

    subtitle = models.CharField(
        verbose_name=_('Subtitle'),
        max_length=255,
        blank=True,
        null=True
    )

    slug = models.SlugField(
        verbose_name=_('Slug'),
        max_length=255,
        unique=True,
        blank=True
    )

    @property
    def is_published(self):
        return self.status == STATUS_CHOICES['Published']

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Author')
    )

    creation_date = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True
    )

    publication_date = models.DateTimeField(
        verbose_name=_('Publication date'),
        blank=True,
        null=True
    )

    last_modified_date = models.DateTimeField(
        verbose_name=_('Last modified date'),
        auto_now=True
    )

    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Can contain raw HTML.'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.slug])

    def __unicode__(self):
        return u'%s' % (self.title)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self.title, Article)
        super(Article, self).save(*args, **kwargs)


class CustomUser(GaeAbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES_TUPLE = (
        (ROLE_CHOICES['Administrator'], _('Administrator')),
        (ROLE_CHOICES['Editor'], _('Editor')),
        (ROLE_CHOICES['Author'], _('Author')),
        (ROLE_CHOICES['Contributor'], _('Contributor')),
        (ROLE_CHOICES['Follower'], _('Follower'))
    )

    role = models.IntegerField(
        verbose_name=_('Role'),
        choices=ROLE_CHOICES_TUPLE,
        default=ROLE_CHOICES['Follower']
    )

    nickname = models.CharField(
        verbose_name=_('Nickname'),
        max_length=50,
        blank=True,
        null=True,
    )

    biographical_info = models.TextField(
        verbose_name=_('Biographical Info'),
        help_text=_('Can contain raw HTML.'),
        blank=True,
        null=True,
    )

    slug = models.SlugField(
        verbose_name=_('Slug'),
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    def __unicode__(self):
        return u"%s" % self.email

    def save(self, *args, **kwargs):
        if self.nickname and not self.slug:
            self.slug = unique_slug(self.nickname, CustomUser)
        super(CustomUser, self).save(*args, **kwargs)

    class Meta:
        app_label = "blog"
        swappable = 'AUTH_USER_MODEL'
        verbose_name = _('user')
        verbose_name_plural = _('users')

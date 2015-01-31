import datetime
from collections import Counter

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext as _u
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Article(models.Model):

    title = models.CharField(
        verbose_name=_('Title'),
        max_length=255
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
        blank=True,
        help_text=_(
            'If changed, the URL will change.'
        )
    )
    is_published = models.BooleanField(
        verbose_name=_('Is published'),
        default=False
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Author')
    )
    creation_date = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True
    )
    publication_date = models.DateTimeField(
        verbose_name=_('Publication date')
    )
    last_modified_date = models.DateTimeField(
        verbose_name=_('Last modified date'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')

    def get_absolute_url(self):
        return reverse('articles:detail', args=[self.slug])

    def __unicode__(self):
        return u'%s' % (self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)


class SingletonModelManager(models.Manager):

    def get(self, *args, **kwargs):
        obj, created = super(
            SingletonModelManager, self).get_or_create(**kwargs)
        return obj


class SingletonModel(models.Model):

    '''
    All subclasses should be cached
    '''
    objects = SingletonModelManager()

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_global(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        abstract = True


class SiteConfiguration(SingletonModel):
    site_name = models.CharField(
        max_length=50,
        default='Lightweight Blog',
        verbose_name=_('Site Name')
    )
    heading = models.CharField(
        max_length=50,
        default='Clean Blog',
        verbose_name=_('Heading Name')
    )
    subheading = models.CharField(
        max_length=50,
        default='A Clean Blog Theme by Start Bootstrap',
        verbose_name=_('Subheading Name')
    )
    footer = models.CharField(
        max_length=50,
        default='Copyright &copy; Your Website 2015',
        verbose_name=_('Footer')
    )
    twitter_address = models.CharField(
        max_length=50,
        verbose_name=_('Twitter address'),
        blank=True,
        null=True
    )
    facebook_address = models.CharField(
        max_length=50,
        verbose_name=_('facebook address'),
        blank=True,
        null=True
    )
    github_address = models.CharField(
        max_length=50,
        verbose_name=_('github address'),
        blank=True,
        null=True
    )

    def __unicode__(self):
        return _u('Global Configuration')

    class Meta:
        verbose_name = _('Global Configuration')
        verbose_name_plural = _('Global Configuration')

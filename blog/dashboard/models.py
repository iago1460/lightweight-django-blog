from django.db import models
from django.utils.translation import ugettext as _u, ugettext_lazy as _


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
        max_length=100,
        default='A Clean Blog Theme by Start Bootstrap',
        verbose_name=_('Subheading Name')
    )

    footer = models.TextField(
        default='Copyright &copy; Your Website 2015',
        verbose_name=_('Footer'),
        help_text=_('Can contain raw HTML.')
    )

    twitter_address = models.CharField(
        max_length=255,
        verbose_name=_('Twitter address'),
        blank=True,
        null=True
    )

    facebook_address = models.CharField(
        max_length=255,
        verbose_name=_('facebook address'),
        blank=True,
        null=True
    )

    github_address = models.CharField(
        max_length=255,
        verbose_name=_('github address'),
        blank=True,
        null=True
    )

    def __unicode__(self):
        return _u('Global Configuration')

    class Meta:
        verbose_name = _('Global Configuration')
        verbose_name_plural = _('Global Configuration')

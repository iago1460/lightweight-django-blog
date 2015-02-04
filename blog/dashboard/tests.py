from djangae.contrib.gauth.backends import AppEngineUserAPI
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.template import Template, Context
from django.test import TestCase
from django.test.client import RequestFactory

from blog.dashboard.decorators import has_permission_level, login_required
from blog.dashboard.models import SiteConfiguration
from blog.utils import ROLE_CHOICES
from google.appengine.api import users


class DecoratorTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.backend = AppEngineUserAPI()

        self.anonymouse_user = AnonymousUser()

        self.administrator_user = get_user_model().objects.create(
            username='000000000000000000001',
            email='1@example.com',
            role=ROLE_CHOICES['Administrator']
        )
        self.editor_user = get_user_model().objects.create(
            username='000000000000000000002',
            email='2@example.com',
            role=ROLE_CHOICES['Editor']
        )
        self.author_user = get_user_model().objects.create(
            username='000000000000000000003',
            email='3@example.com',
            role=ROLE_CHOICES['Author']
        )
        self.contributor_user = get_user_model().objects.create(
            username='000000000000000000004',
            email='4@example.com',
            role=ROLE_CHOICES['Contributor']
        )
        self.follower = get_user_model().objects.create(
            username='000000000000000000005',
            email='5@example.com',
            role=ROLE_CHOICES['Follower']
        )

    def test_login_required_decorator(self):
        @login_required
        def a_view(request):
            return HttpResponse()

        def do_request(user):
            request = self.factory.get('/rand')
            request.user = user
            return a_view(request)

        self.assertEqual(do_request(self.anonymouse_user).status_code, 302)
        self.assertEqual(do_request(self.follower).status_code, 200)

    def do_request(self, user, required_level):
        @has_permission_level(required_level)
        def a_view(request):
            return HttpResponse()

        request = self.factory.get('/rand')
        request.user = user
        return a_view(request)

    def test_has_permission_level_decorator(self):
        self.assertEqual(
            self.do_request(self.administrator_user, 'Contributor').status_code, 200)
        self.assertEqual(
            self.do_request(self.editor_user, 'Contributor').status_code, 200)
        self.assertEqual(
            self.do_request(self.author_user, 'Contributor').status_code, 200)
        self.assertEqual(
            self.do_request(self.contributor_user, 'Contributor').status_code, 200)
        self.assertEqual(
            self.do_request(self.follower, 'Contributor').status_code, 302)

        self.assertEqual(
            self.do_request(self.administrator_user, 'Author').status_code, 200)
        self.assertEqual(
            self.do_request(self.editor_user, 'Author').status_code, 200)
        self.assertEqual(
            self.do_request(self.author_user, 'Author').status_code, 200)
        self.assertEqual(
            self.do_request(self.contributor_user, 'Author').status_code, 302)
        self.assertEqual(
            self.do_request(self.follower, 'Author').status_code, 302)

        self.assertEqual(
            self.do_request(self.administrator_user, 'Editor').status_code, 200)
        self.assertEqual(
            self.do_request(self.editor_user, 'Editor').status_code, 200)
        self.assertEqual(
            self.do_request(self.author_user, 'Editor').status_code, 302)
        self.assertEqual(
            self.do_request(self.contributor_user, 'Editor').status_code, 302)
        self.assertEqual(
            self.do_request(self.follower, 'Editor').status_code, 302)

        self.assertEqual(
            self.do_request(self.administrator_user, 'Administrator').status_code, 200)
        self.assertEqual(
            self.do_request(self.editor_user, 'Administrator').status_code, 302)
        self.assertEqual(
            self.do_request(self.author_user, 'Administrator').status_code, 302)
        self.assertEqual(
            self.do_request(self.contributor_user, 'Administrator').status_code, 302)
        self.assertEqual(
            self.do_request(self.follower, 'Administrator').status_code, 302)


class SingletonModelTests(TestCase):

    def test_autocreate(self):
        self.assertEqual(SiteConfiguration.objects.count(), 0)
        config = SiteConfiguration.get_global()
        self.assertEqual(SiteConfiguration.objects.count(), 1)

    def test_singleton(self):
        self.assertEqual(SiteConfiguration.objects.count(), 0)
        config = SiteConfiguration.objects.create(site_name='Blog')
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        with self.assertRaises(IntegrityError):
            config2 = SiteConfiguration.objects.create(site_name='Blog 2')
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        config3 = SiteConfiguration.get_global()
        self.assertEqual(config.pk, config3.pk)

    def test_get_global_model_tag(self):
        self.assertEqual(SiteConfiguration.objects.count(), 0)
        site_name = 'Blog'
        SiteConfiguration.objects.create(site_name=site_name)
        out = Template(
            "{% load global_settings_extras %}"
            "{% get_global_model 'dashboard.SiteConfiguration' as site_config %}"
            "{{ site_config.site_name }}"
        ).render(Context())
        self.assertEqual(site_name, out)

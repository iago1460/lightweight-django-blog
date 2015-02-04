from django.contrib.auth import get_user_model
from django.test import TestCase

from blog.utils import ROLE_CHOICES, STATUS_CHOICES
from blog.models import Article


class ArticleTests(TestCase):

    def setUp(self):
        self.author = get_user_model().objects.create(
            username='000000000000000000001',
            email='1@example.com',
            role=ROLE_CHOICES['Author']
        )

    def test_article_slug(self):
        title_article = 'Article'
        article1 = Article.objects.create(
            status=STATUS_CHOICES['Draft'],
            title=title_article,
            author=self.author
        )
        self.assertEqual('article', article1.slug)

        article2 = Article.objects.create(
            status=STATUS_CHOICES['Draft'],
            title=title_article,
            author=self.author
        )
        self.assertEqual('article_1', article2.slug)

    def test_published(self):
        article = Article.objects.create(
            status=STATUS_CHOICES['Draft'],
            title='Article 1',
            author=self.author
        )
        self.assertFalse(article.is_published)

        article.status = STATUS_CHOICES['Published']
        self.assertTrue(article.is_published)


class CustomUser(TestCase):

    def test_slug(self):
        author_name = 'Name'
        author = get_user_model().objects.create(
            email='1@example.com',
            role=ROLE_CHOICES['Author']
        )
        self.assertIsNone(author.slug)

        author.nickname = author_name
        author.save()
        self.assertEqual('name', author.slug)

        author2 = get_user_model().objects.create(
            nickname=author_name,
            email='2@example.com',
            role=ROLE_CHOICES['Author']
        )
        self.assertEqual('name_1', author2.slug)

        author3 = get_user_model().objects.create(
            nickname=author_name,
            email='3@example.com',
            role=ROLE_CHOICES['Author']
        )
        self.assertEqual('name_2', author3.slug)

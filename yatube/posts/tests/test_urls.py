from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from collections import namedtuple

from ..models import Post, Group


User = get_user_model()


class PostUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='test-slug',
            description='Описание для теста',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Пост для теста' * 5,
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

        cls.Urls = namedtuple(
            'Urls',
            'Index Group_list Profile '
            'Post_detail Create_post Edit_post Unexisting_page'
        )
        cls.urls = cls.Urls(
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.author}/',
            f'/posts/{cls.post.id}/',
            '/create/',
            f'/posts/{cls.post.id}/edit/',
            '/unexisting_page'
        )

    def test_correct_urls(self):
        for i in range(0, 4):
            address = self.urls[i]
            with self.subTest():
                response = Client().get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_incorrect_urls(self):
        response = Client().get(self.urls.Unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_urls(self):
        response = self.authorized_client.get(self.urls.Create_post)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        cache.clear()
        templates_url_names = {
            self.urls.Index: 'posts/index.html',
            self.urls.Group_list: 'posts/group_list.html',
            self.urls.Profile: 'posts/profile.html',
            self.urls.Post_detail: 'posts/post_detail.html',
            self.urls.Edit_post: 'posts/create_post.html',
            self.urls.Create_post: 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_edit_post_authorized_author(self):
        response = self.authorized_client.get(
            reverse('posts:post_create',)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_edit_authorized_not_author_redirection(self):
        response = Client().post(
            reverse('posts:post_edit', kwargs={'post_id': '1'},)
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

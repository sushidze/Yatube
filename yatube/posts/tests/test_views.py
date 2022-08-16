import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Post, Group, Comment


User = get_user_model()

TEMP_MEDIA_ROOT = os.path.join(settings.BASE_DIR, '123/')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='test-slug',
            description='Описание для теста',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Пост для теста' * 5,
            pub_date='01.08.2022',
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='комментарий'
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        cache.clear()
        templates_page_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        first_object_text = first_object.text
        first_object_img = first_object.image
        self.assertEqual(first_object_text, 'Пост для теста' * 5)
        self.assertEqual(first_object_img, self.post.image)

    def test_group_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            )
        )
        first_object_img = response.context['page_obj'][0].image
        self.assertEqual(
            response.context.get('group').title,
            'Группа для теста'
        )
        self.assertEqual(
            response.context.get('group').description,
            'Описание для теста'
        )
        self.assertEqual(first_object_img, self.post.image)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'author'}
            )
        )
        first_object = response.context['page_obj'][0]
        first_object_author = first_object.author.username
        self.assertEqual(first_object_author, 'author')
        first_object_img = response.context['page_obj'][0].image
        self.assertEqual(first_object_img, self.post.image)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        first_object = response.context['post']
        first_object_text = first_object.text
        self.assertEqual(first_object_text, 'Пост для теста' * 5)
        first_object_img = first_object.image
        self.assertEqual(first_object_img, self.post.image)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        first_object = response.context['post']
        first_object_text = first_object.text
        self.assertEqual(first_object_text, 'Пост для теста' * 5)

    def test_index_show_new_post(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        first_object_text = first_object.text
        first_object_group = first_object.group.title
        first_object_author = first_object.author.username
        self.assertEqual(first_object_text, 'Пост для теста' * 5)
        self.assertEqual(first_object_author, 'author')
        self.assertEqual(first_object_group, 'Группа для теста')

    def test_group_list_show_new_post(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            )
        )
        first_object = response.context['page_obj'][0]
        first_object_text = first_object.text
        first_object_group = first_object.group.title
        first_object_author = first_object.author.username
        self.assertEqual(first_object_text, 'Пост для теста' * 5)
        self.assertEqual(first_object_author, 'author')
        self.assertEqual(first_object_group, 'Группа для теста')

    def test_profile_show_new_post(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'author'}
            )
        )
        first_object = response.context['page_obj'][0]
        first_object_text = first_object.text
        first_object_group = first_object.group.title
        first_object_author = first_object.author.username
        self.assertEqual(first_object_text, 'Пост для теста' * 5)
        self.assertEqual(first_object_author, 'author')
        self.assertEqual(first_object_group, 'Группа для теста')

    def test_follow_index_show_new_post_for_auth(self):
        cache.clear()
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': 'author'}
        ))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        first_object_text = first_object.text
        first_object_group = first_object.group.title
        first_object_author = first_object.author.username
        self.assertEqual(first_object_text, 'Пост для теста' * 5)
        self.assertEqual(first_object_author, 'author')
        self.assertEqual(first_object_group, 'Группа для теста')

    def test_show_new_comment(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        first_comment = response.context['comments'][0]
        first_comment_text = first_comment.text
        first_comment_author = first_comment.author.username
        self.assertEqual(first_comment_text, 'комментарий')
        self.assertEqual(first_comment_author, 'author')

    def test_cache_index(self):
        before_create_post = self.authorized_client.get(
            reverse('posts:index'))
        first_item_before = before_create_post.content
        Post.objects.create(
            author=self.author,
            text='Проверка кэша',
            group=self.group
        )
        after_create_post = self.authorized_client.get(reverse('posts:index'))
        first_item_after = after_create_post.content
        self.assertEqual(first_item_after, first_item_before)
        cache.clear()
        after_clear = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_item_after, after_clear)

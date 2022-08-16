import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Comment, Follow


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='test-slug',
            description='Описание для теста',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Пост для теста' * 5,
            pub_date='01.08.2022'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='комментарий'
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

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'image': self.uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'author'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст',
            'group': f'{self.post.group.id}',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            form_data['text']
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_unauth_user_cant_publish_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_unauth_user_cant_publish_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_create_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_auth_user_can_subscribe_and_unsubscribe(self):
        count_followers = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': 'user'}
        ))
        self.assertEqual(Follow.objects.count(), count_followers + 1)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': 'user'}
        ))
        self.assertEqual(Follow.objects.count(), count_followers)
        self.assertEqual(Follow.objects.count(), count_followers)
        self.assertEqual(self.author.follower.count(), 0)
        'Проверьте, что правильно считается подписки'
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': 'author'}
        ))
        self.assertEqual(self.author.follower.count(), 0)
        'Проверьте, что нельзя подписаться на самого себя'

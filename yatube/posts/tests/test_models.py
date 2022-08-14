from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='Слаг для теста',
            description='Описание для теста',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост для теста' * 5,
        )

    def test_correct_str(self):
        post = PostModelTest.post
        group = PostModelTest.group
        len_text = str(post)
        base_len_text = post.text[:settings.CHARS_LIMIT]
        self.assertEqual(
            len_text,
            base_len_text,
            '__str__ Post  работает не правильно'
        )
        group_title = group.title
        group_str = str(group)
        self.assertEqual(group_title, group_str)

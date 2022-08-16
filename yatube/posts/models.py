from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        help_text='Содержание вашего поста',
        verbose_name='Текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Выберите группу',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='group'

    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:settings.CHARS_LIMIT]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        default='',
        help_text='Напишите ваш комментарий',
        verbose_name='Текст комментария'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )
    constraints = [
        models.UniqueConstraint(
            fields=('user', 'author'), name="unique_followers"
        ),
        models.CheckConstraint(
            check=~models.Q(user=models.F('author')),
            name='do not selffollow'),
    ]

# Generated by Django 2.2.16 on 2022-08-08 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AddField(
            model_name='comment',
            name='text',
            field=models.TextField(default='', help_text='Напишите ваш комментарий', verbose_name='Текст комментария'),
        ),
    ]

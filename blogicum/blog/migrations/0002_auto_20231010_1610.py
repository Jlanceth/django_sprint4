# Generated by Django 3.2.16 on 2023-10-10 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_squashed_0010_auto_20231010_0111'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'default_related_name': 'comment', 'ordering': ('created_at',)},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'default_related_name': 'posts', 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]

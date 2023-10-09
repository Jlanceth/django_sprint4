from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()

CHAR_STRING_LENGHT = 256
SLUG_STRING_LENGHT = 64


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text=('Снимите галочку, '
                   'чтобы скрыть публикацию.'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(
        max_length=CHAR_STRING_LENGHT,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        max_length=SLUG_STRING_LENGHT,
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры,'
                   ' дефис и подчёркивание.'),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        max_length=CHAR_STRING_LENGHT,
        verbose_name='Название места',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(
        max_length=CHAR_STRING_LENGHT,
        verbose_name='Заголовок',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в'
                   ' будущем — можно делать '
                   'отложенные публикации.'),
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        null=True, on_delete=models.SET_NULL,
        verbose_name='Местоположение',
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='posts',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Добавьте комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Комментарий от {self.author} к "{self.post}"'

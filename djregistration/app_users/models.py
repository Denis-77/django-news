from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    CITY_CHOICES = [
        ('mos', 'Москва'),
        ('spb', 'Санкт-Петербург'),
        ('min', 'Минск'),
        ('ebg', 'Екатеринбург'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(verbose_name='Номер телефона')
    city = models.CharField(verbose_name='Город', choices=CITY_CHOICES, max_length=3)
    is_verified = models.BooleanField(verbose_name='Флаг верификации', default=False)
    news_count = models.IntegerField(verbose_name='Количество опубликованных новостей', default=0)

    class Meta:
        permissions = (
            ('can_verify', 'Может верифицировать других пол-ей'),
            ('is_moderator', 'Флаг модератора'),
        )

    def __str__(self):
        return self.user.__str__()


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Новостной тег')

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')
    content = models.CharField(max_length=5000, verbose_name='Содержание')
    creation_date = models.DateField(verbose_name='Дата создания', auto_now_add=True, db_index=True)
    edit_date = models.DateField(verbose_name='Дата редактирования', auto_now=True)
    is_published = models.BooleanField(verbose_name='Опубликовано', default=False)
    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE)
    news_tag = models.ManyToManyField(Tag, verbose_name='Новостной тег', blank=True)

    def __str__(self):
        cut_news = self.title
        if len(cut_news) > 25:
            cut_news = self.title[:25]
        return '{author} ||| {news}'.format(
            news=cut_news,
            author=self.user
        )

    class Meta:
        verbose_name_plural = 'News'
        ordering = ['-creation_date']
        permissions = (
            ('can_approve', 'Может одобрять публикацию'),
        )


class Comment(models.Model):
    username = models.CharField(max_length=50, verbose_name='Имя пользователя')
    comment_text = models.CharField(max_length=500, verbose_name='Текст комментария')
    news = models.ForeignKey('News', on_delete=models.CASCADE, verbose_name='Новость')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', default=None, null=True)

    def less_comment(self):
        comment = self.comment_text
        if len(comment) > 15:
            comment = self.comment_text[:15] + '...'
        return comment

    def __str__(self):
        less_comment = self.less_comment()
        return '{n}){who} --- {what}'.format(n=self.id, who=self.username, what=less_comment)



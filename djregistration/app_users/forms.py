from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from app_users.models import News, Comment, Tag


class RegistrationForm(UserCreationForm):
    CITY_CHOICES = [
        ('mos', 'Москва'),
        ('spb', 'Санкт-Петербург'),
        ('min', 'Минск'),
        ('ebg', 'Екатеринбург'),
    ]
    first_name = forms.CharField(max_length=30, label='Имя', required=False)
    last_name = forms.CharField(max_length=50, label='Фамилия', required=False)
    email = forms.EmailField(max_length=254)
    phone_number = forms.IntegerField(label='Номер телефона', max_value=(10**14 - 1), localize=True)
    city = forms.ChoiceField(label='Город', choices=CITY_CHOICES)
    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput,
        help_text='- Ваш пароль не должен быть слишком похож на другую личную информацию.\n'
                  '- Ваш пароль должен содержать не менее 8 символов.\n'
                  '- Ваш пароль не может быть широко используемым паролем.\n'
                  '- Ваш пароль не может быть полностью числовым.'
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        strip=False,
        help_text='Введите пароль ещё раз',
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {'username': 'Логин'}
        help_texts = {'username': 'Обязательное. Латиницей, не более 150 символов'}


def choices(elem):
    if len(elem):
        return forms.CheckboxSelectMultiple(choices=elem)
    return forms.TextInput()


class CreateNews(forms.ModelForm):

    class Meta:

        model = News
        fields = ['title', 'content', 'news_tag']
        widgets = {
            'title': forms.Textarea(attrs={'cols': 100, 'rows': 2}),
            'content': forms.Textarea(attrs={'cols': 100, 'rows': 10}),
            # 'news_tag': forms.CheckboxSelectMultiple(choices=Tag.objects.all())
            'news_tag': choices(Tag.objects.all())
        }


class CommentFormAuth(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={'cols': 50, 'rows': 10}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['username', 'comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={'cols': 50, 'rows': 10}),
        }


class VerifyForm(forms.Form):
    verify = forms.BooleanField(required=False)
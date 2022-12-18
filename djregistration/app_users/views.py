from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LogoutView, LoginView

from app_users.models import News, Profile, Comment, Tag
from app_users.forms import RegistrationForm, CreateNews, CommentForm, CommentFormAuth


class AllNewsView(View):
    def get(self, request):
        all_news = News.objects.filter(is_published=True).all()
        if request.GET.get('filter'):
            if request.GET.get('filter') == '1':
                last = all_news.first().edit_date
                all_news = all_news.filter(creation_date=last).all()
            elif request.GET.get('filter') == '2':
                tag = Tag.objects.get(id=3)
                all_news = all_news.filter(news_tag=tag)
            elif request.GET.get('filter') == '3':
                tag = Tag.objects.get(id=2)
                all_news = all_news.filter(news_tag=tag)
            elif request.GET.get('filter') == '4':
                tag = Tag.objects.get(id=1)
                all_news = all_news.filter(news_tag=tag)

        is_moderator = request.user.has_perm('app_users.is_moderator')
        return render(request, 'app_users/index.html', context={
            'all_news': all_news,
            'is_moderator': is_moderator,
        })


class DetailNews(View):
    def get(self, request, news_id):
        news = News.objects.get(id=news_id)
        user = request.user
        if user.is_authenticated:
            form = CommentFormAuth()
        else:
            form = CommentForm()
        comments = Comment.objects.filter(news=news).all()
        return render(request, 'app_users/news_item.html', {
            'form': form,
            'news': news,
            'comments': comments,
            'user': user,
        })

    def post(self, request, news_id):
        news = News.objects.get(id=news_id)
        user = request.user
        comments = Comment.objects.filter(news=news).all()
        if user.is_authenticated:
            form = CommentFormAuth(request.POST)
            if form.is_valid():
                Comment.objects.create(**form.cleaned_data, user=user, news=news)
                return redirect('../../news/{id}/'.format(id=news_id))
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                Comment.objects.create(**form.cleaned_data, news=news)
                return redirect('../../news/{id}/'.format(id=news_id))
        return render(request, 'app_users/news_item.html', {
            'form': form,
            'news': news,
            'comments': comments,
            'user': user,
        })


class MyLoginView(LoginView):
    template_name = 'app_users/login.html'


class MyLogoutView(LogoutView):
    next_page = '/'


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')
            city = form.cleaned_data.get('city')
            Profile.objects.create(user=user, city=city, phone_number=phone_number)
            regular_group = Group.objects.get(name='regular_user')
            user.groups.add(regular_group)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'app_users/registration.html', {'form': form})


def account_view(request):
    return render(request, 'app_users/account.html', {'user': request.user})


class CreateView(View):
    def get(self, request):
        if not request.user.has_perm('app_users.add_news'):
            raise PermissionDenied()
        form = CreateNews()
        return render(request, 'app_users/create.html', {'form': form})

    def post(self, request):
        if not request.user.has_perm('app_users.add_news'):
            raise PermissionDenied()
        form = CreateNews(request.POST)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            tag = form.cleaned_data.get('news_tag')
            news = News.objects.create(
                title=title,
                content=content,
                user=user
            )
            news.news_tag.set(tag)
            news.save()
            news_count = user.profile.news_count
            news_count += 1
            user.profile.news_count = news_count
            user.profile.save()
            return redirect('/')
        return render(request, 'app_users/create.html', {'form': form})


class EditNews(View):
    def get(self, request, news_id):
        news = News.objects.get(id=news_id)
        if request.user != news.user:  # Проверка авторства
            raise PermissionDenied()
        form = CreateNews(instance=news)
        return render(request, 'app_users/edit.html', {'form': form, 'news_id': news_id})

    def post(self, request, news_id):
        news = News.objects.get(id=news_id)
        if request.user != news.user:
            raise PermissionDenied()
        form = CreateNews(request.POST, instance=news)
        if form.is_valid():
            tag = form.cleaned_data.get('news_tag')
            news.news_tag.set(tag)
            news.save()
            return redirect('/')
        return render(request, 'app_users/edit.html', {'form': form, 'news_id': news_id})


class ModeratorsOnlyView(View):
    def get(self, request):
        if not request.user.has_perm('app_users.is_moderator'):
            raise PermissionDenied()
        unverified = Profile.objects.filter(is_verified=False).all()
        unpublished = News.objects.filter(is_published=False).all()

        return render(request, 'app_users/moderators_only.html', {
            'unverified': unverified,
            'unpublished': unpublished,
        })

    def post(self, request):
        if not request.user.has_perm('app_users.is_moderator'):
            raise PermissionDenied()
        for key, value in request.POST.items():
            if key.startswith('verify'):
                if not request.user.has_perm('app_users.can_verify'):
                    raise PermissionDenied()
                key = key[6:]
                user_id = int(key)
                profile = Profile.objects.get(id=user_id)
                profile.is_verified = True
                profile.save()
                verified = Group.objects.get(name='verified_users')
                profile.user.groups.add(verified)
            elif key.startswith('publish'):
                if not request.user.has_perm('app_users.can_approve'):
                    raise PermissionDenied()
                key = key[7:]
                news_id = int(key)
                news = News.objects.get(id=news_id)
                if value == 'True':
                    news.is_published = True
                    news.save()
                else:
                    news.delete()
        unverified = Profile.objects.filter(is_verified=False).all()
        unpublished = News.objects.filter(is_published=False).all()
        return render(request, 'app_users/moderators_only.html', {
            'unverified': unverified,
            'unpublished': unpublished,
        })



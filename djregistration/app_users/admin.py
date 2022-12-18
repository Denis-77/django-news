from django.contrib import admin
from app_users.models import Profile, Comment, News, Tag


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone_number', 'city', 'is_verified', 'news_count']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'is_published']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'username', 'news', 'comment_text']
    list_filter = ['news']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
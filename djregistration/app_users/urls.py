from django.urls import path
from app_users.views import *

urlpatterns = [
    path('', AllNewsView.as_view(), name='main'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('registration/', registration_view, name='registration'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('create/', CreateView.as_view(), name='create'),
    path('news/<int:news_id>/edit/', EditNews.as_view(), name='edit'),
    path('news/<int:news_id>/', DetailNews.as_view(), name='news_item'),
    path('account/', account_view, name='account'),
    path('moderator/', ModeratorsOnlyView.as_view(), name='moderators_page')
]
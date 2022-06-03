from django.urls import path
from . import views

# from django.conf.urls import url, include
from django.urls import re_path as url

from django.contrib.auth import views as auth_views
from .views import login_page


urlpatterns = [
    path('', views.home, name='home'),
    path('sign/', views.sign, name='sign'),
    path('question/', views.question, name='question'),
    path('before_question/', views.before_question, name='before_question'),
    path('result/', views.result, name='result'),
    path('video_feed', views.video_feed, name='video_feed'),
    url(r'^signup/$', views.signup, name='signup'),
    path('login/', views.login_page, name='login'),
    path("logout", views.logout_request, name="logout"), 
]

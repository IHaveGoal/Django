# -*- coding:utf-8 -*-
# Author : ZRQ
# Data : 2019/6/19 15:05
from django.urls import path, re_path
from me import views

urlpatterns = [
    re_path('(\w+)/(tag|category|archive)/(.+)/',views.home),
    path('<str:username>/article/<int:pk>/',views.article_detail),
    path('up_down/',views.up_down),
    path('comment/',views.comment),
    re_path('comment_tree/(\d+)/',views.comment_tree),
    re_path('(\w+)/', views.home),
]
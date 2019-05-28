from django.conf.urls import url
from app_book import views

urlpatterns = [

    url(r'^test/', views.test, name='test'),

]
from django.urls import path, include
from . import views

app_name = 'chat_bot'

urlpatterns = [
    path('', views.chat_bot, name='chat_bot'),
]
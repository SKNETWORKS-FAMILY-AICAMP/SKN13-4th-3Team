from django.urls import path
from . import views
from config import settings
from django.conf.urls.static import static

app_name = 'chat_bot'

urlpatterns = [
    path('', views.chat_list_view, name='chat_list'),
    path('new/', views.new_chat_session, name='new_chat_session'),
    path('conversation/', views.chat_conversation, name='chat_conversation'),
    path('conversation/<int:session_id>/', views.chat_conversation, name='chat_conversation_with_id'),
    path('clear/', views.clear_chat, name='clear_chat'),
]

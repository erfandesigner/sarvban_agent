from django.urls import path,include
from .views import chat, chat_room

urlpatterns = [
    path("chat", chat, name="chat"),

    path('', chat_room, name='chat_room'),
]

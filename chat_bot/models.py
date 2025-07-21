from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    """
    각 사용자의 전체 대화 세션을 나타냅니다.
    하나의 세션 안에는 여러 개의 메시지가 포함됩니다.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Session for {self.user.username}"

class ChatMessage(models.Model):
    """
    개별 메시지(사용자의 질문 또는 AI의 답변)를 저장합니다.
    """
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    is_from_user = models.BooleanField(default=True) # True면 사용자, False면 AI
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "User" if self.is_from_user else "AI"
        return f"{sender}: {self.content[:50]}"